from osgeo import gdal, ogr, osr
from shapely.geometry import shape

from gobcore.utils import ProgressTicker

from gobexport.exporter.utils import split_field_reference, get_entity_value


gdal.UseExceptions()


def add_field_definitions(layer, fieldnames):
    """Adds all fieldnames to a shape layer definition

    :param layer: A shape layer object
    :param fieldnames: A list of fieldnames to create
    :return:
    """
    for fieldname in fieldnames:
        fielddef = ogr.FieldDefn(fieldname, ogr.OFTString)
        layer.CreateField(fielddef)


def create_geometry(entity_geometry):
    # Add geometrie
    poly = ogr.CreateGeometryFromWkt(shape(entity_geometry).wkt)

    # Force geometriecollection to polygon
    if poly.GetGeometryType() == ogr.wkbGeometryCollection:
        poly = ogr.ForceToPolygon(poly)

    return poly


def _get_geometry_type(entity):
    # Try to get the geometry type from the first record
    try:
        geometry_type = create_geometry(entity['geometrie']).GetGeometryType()
    except (KeyError, AttributeError) as e:
        geometry_type = ogr.wkbPolygon
    return geometry_type


def esri_exporter(api, file, format=None, append=False):
    """ESRI Exporter

    This function will transform the output of an API to ESRI shape files. The
    result will be 4 files (.shp, .dbf, .shx and .prj), which all contain some
    required data.

    It uses the python bindings to the GDAL library.

    :param api: The encapsulated API as an iterator
    :param file: The main file (.shp) to write to
    :param format: The mapping of the API output to ESRI fields as defined in the
    export config. The max length of an esri fieldname is 10 characters.
    """
    if append:
        raise NotImplementedError("Appending not implemented for this exporter")

    row_count = 0
    driver = ogr.GetDriverByName("ESRI Shapefile")
    dstfile = driver.CreateDataSource(file)

    # Set spatialref to RD
    spatialref = osr.SpatialReference()
    spatialref.ImportFromEPSG(28992)

    with ProgressTicker(f"Export entities", 10000) as progress:
        # Get records from the API and build the esri file
        for entity in api:

            # On the first entity determine the type of shapefile we need to export
            if row_count == 0:
                # Please note that it will fail if a file with the same name already exists
                geometry_type = _get_geometry_type(entity)
                dstlayer = dstfile.CreateLayer("layer", spatialref, geom_type=geometry_type)

                # Add all field definitions
                add_field_definitions(dstlayer, format.keys())

            feature = ogr.Feature(dstlayer.GetLayerDefn())

            if entity['geometrie']:
                feature.SetGeometry(create_geometry(entity['geometrie']))

            # Add all fields from the config to the file
            for attribute_name, source in format.items():
                mapping = split_field_reference(source)
                value = get_entity_value(entity, mapping)

                # Esri expects an emtpy string when value is None
                value = '' if value is None else value

                feature.SetField(attribute_name, value)

            dstlayer.CreateFeature(feature)

            feature.Destroy()
            row_count += 1
            progress.tick()

    dstfile.Destroy()

    return row_count
