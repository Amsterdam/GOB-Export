from osgeo import gdal, ogr, osr
from shapely.geometry import shape


gdal.UseExceptions()


def esri_exporter(api, file, format=None):
    row_count = 0
    driver = ogr.GetDriverByName("ESRI Shapefile")
    dstfile = driver.CreateDataSource(file)

    # Set spatialref to RD
    spatialref = osr.SpatialReference()
    spatialref.ImportFromEPSG(28992)

    # Please note that it will fail if a file with the same name already exists
    dstlayer = dstfile.CreateLayer("layer", spatialref, geom_type=ogr.wkbPolygon)

    # Add all field definitions
    for fieldname in format.values():
        fielddef = ogr.FieldDefn(fieldname, ogr.OFTString)
        dstlayer.CreateField(fielddef)

    # Get records from the API and build the esri file
    for entity in api:
        feature = ogr.Feature(dstlayer.GetLayerDefn())

        # Add geometrie
        poly = ogr.CreateGeometryFromWkt(shape(entity['geometrie']).wkt)

        # Force geometriecollection to polygon
        if poly.GetGeometryType() == ogr.wkbGeometryCollection:
            poly = ogr.ForceToPolygon(poly)

        feature.SetGeometry(poly)

        # Add all fields from the config to the file
        for source, mapping in format.items():
            feature.SetField(mapping, entity.get(source, ''))

        dstlayer.CreateFeature(feature)

        row_count += 1
    feature.Destroy()
    dstfile.Destroy()

    return row_count
