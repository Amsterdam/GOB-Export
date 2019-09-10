from shapely.geometry import shape


def format_geometry(value):
    """Returns geometry as wkt string for file exports

    :param value item:
    :return:
    """
    if isinstance(value, dict):
        # Transform geojson to wkt, if None return an empty string
        return shape(value).wkt
    else:
        return value if value else ''
