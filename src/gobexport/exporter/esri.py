import os

from osgeo import gdal, ogr, osr
from shapely.geometry import shape

from gobcore.utils import ProgressTicker

from gobexport.exporter.utils import split_field_reference, get_entity_value
from gobexport.filters.entity_filter import EntityFilter


gdal.UseExceptions()
os.environ['SHAPE_ENCODING'] = "utf-8"

spatialref_rd = osr.SpatialReference()
spatialref_rd.ImportFromEPSG(28992)

spatialref_wgs84 = osr.SpatialReference()
spatialref_wgs84.ImportFromEPSG(4326)

transform = osr.CoordinateTransformation(spatialref_rd, spatialref_wgs84)
COORDINATE_PRECISION = 7


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
    assert entity_geometry is not None
    # Get geometry from GEOJSON or WKTstring (GraphQLStreaming)
    geometry_wkt = shape(entity_geometry).wkt if isinstance(entity_geometry, dict) else entity_geometry
    # Add geometrie
    poly = ogr.CreateGeometryFromWkt(geometry_wkt)

    # Force geometriecollection to polygon
    if poly and poly.GetGeometryType() == ogr.wkbGeometryCollection:
        poly = ogr.ForceToPolygon(poly)

    return poly


def _get_geometry_type(entity_geometry):
    # Try to get the geometry type from the first record, default to Polygon
    geometry_type = create_geometry(entity_geometry).GetGeometryType()
    return geometry_type


def esri_exporter(api, file, format=None, append=False, filter: EntityFilter=None):
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

    geometry_field = format['geometrie'] if 'geometrie' in format.keys() else 'geometrie'

    with ProgressTicker(f"Export entities", 10000) as progress:
        # Get records from the API and build the esri file
        for entity in api:
            if filter and not filter.filter(entity):
                continue

            entity_geometry = get_entity_value(entity, geometry_field)

            # On the first entity determine the type of shapefile we need to export
            if row_count == 0:
                # Please note that it will fail if a file with the same name already exists
                geometry_type = _get_geometry_type(entity_geometry)
                dstlayer = dstfile.CreateLayer("layer", spatialref, geom_type=geometry_type)

                # Add all field definitions, but skip geometrie
                all_fields = {k: v for k, v in format.items() if k is not geometry_field}
                add_field_definitions(dstlayer, all_fields.keys())

            feature = ogr.Feature(dstlayer.GetLayerDefn())
            if entity_geometry:
                feature.SetGeometry(create_geometry(entity_geometry))

            for attribute_name, source in all_fields.items():
                mapping = split_field_reference(source)
                value = get_entity_value(entity, mapping)

                # Esri expects an emtpy string when value is None
                value = '' if value is None else value

                feature.SetField(attribute_name, value)

            dstlayer.CreateFeature(feature)

            feature.Destroy()
            row_count += 1
            progress.tick()

    # When no rows are returned no layer has been made, so create it afterwards to make sure files exist
    dstlayer = dstfile.CreateLayer("layer", spatialref, geom_type=ogr.wkbPolygon) if row_count == 0 else dstlayer

    dstfile.Destroy()

    return row_count


def get_centroid(wkt):
    """Get Centroid from WKT geomentry.

    We need POINT to be able to get coordinates.
    """
    return ogr.CreateGeometryFromWkt(wkt).Centroid()


def get_x(wkt):
    """Get X coordinate from Centroid of WKT geomentry.

    Also cast it to integer.
    """
    return int(get_centroid(wkt).GetX())


def get_y(wkt):
    """Get Y coordinate from Centroid of WKT geomentry.

    Also cast it to integer.
    """
    return int(get_centroid(wkt).GetY())


def get_longitude(wkt):
    """Get Longitude coordinate (WGS84) from Centroid of WKT geomentry.

    Also round it to COORDINATE_PRECISION (decimal percision).
    """
    centroid = get_centroid(wkt)
    centroid.Transform(transform)
    return round(centroid.GetX(), COORDINATE_PRECISION)


def get_latitude(wkt):
    """Get Latitude coordinate (WGS84) from Centroid of WKT geomentry.

    Also round it to COORDINATE_PRECISION (decimal percision).
    """
    centroid = get_centroid(wkt)
    centroid.Transform(transform)
    return round(centroid.GetY(), COORDINATE_PRECISION)
