from gdal import ogr

import os


def create_shp(shp_file_dir, overwrite=True, *args, **kwargs):
    """
    Create a new shapefile with a defined geometry type (optional)
    :param shp_file_dir: STR of the (relative) shapefile directory (ends on ".shp")
    :param overwrite: [optional] BOOL - if True, existing files are overwritten
    :kwarg layer_name: [optional] STR of the layer_name - if None: no layer will be created
    :kwarg layer_type: [optional] STR ("point, "line", or "polygon") of the layer_name - if None: no layer will be created
    :output: ogr shapefile (osgeo.ogr.DataSource)
    """
    shp_driver = ogr.GetDriverByName("ESRI Shapefile")

    # check if output file exists if yes delete it
    if os.path.exists(shp_file_dir) and overwrite:
        shp_driver.DeleteDataSource(shp_file_dir)

    # create and return new shapefile object
    new_shp = shp_driver.CreateDataSource(shp_file_dir)

    # create layer if layer_name and layer_type are provided
    if kwargs.get("layer_name") and kwargs.get("layer_type"):
        # create dictionary of ogr.SHP-TYPES
        geometry_dict = {"point": ogr.wkbPoint,
                         "points": ogr.wkbMultiPoint,
                         "line": ogr.wkbMultiLineString,
                         "polygon": ogr.wkbMultiPolygon}
        # create layer
        try:
            new_shp.CreateLayer(str(kwargs.get("layer_name")),
                                geom_type=geometry_dict[str(kwargs.get("layer_type").lower())])
        except KeyError:
            print("Error: Invalid layer_type provided (must be 'point', 'line', or 'polygon').")
        except TypeError:
            print("Error: layer_name and layer_type must be string.")
    return new_shp


def get_geom_description(layer):
    """
    Get the WKB Geometry Type as string from a shapefile layer
    :param layer: osgeo.ogr.Layer
    :output: STR of wkbGEOMETRY-TYPE
    """
    type_dict = {0: "wkbUnknown", 1: "wkbPoint", 2: "wkbLineString", 3: "wkbPolygon",
                 4: "wkbMultiPoint", 5: "wkbMultiLineString", 6: "wkbMultiPolygon",
                 7: "wkbGeometryCollection", 8: "wkbCircularString", 9: "wkbCompoundCurve",
                 10: "wkbCurvePolygon", 11: "wkbMultiCurve", 12: "wkbMultiSurface",
                 13: "wkbCurve", 14: "wkbSurface", 15: "wkbPolyhedralSurface", 16: "wkbTIN",
                 17: "wkbTriangle", 100: "wkbNone", 101: "wkbLinearRing", 1008: "wkbCircularStringZ",
                 1009: "wkbCompoundCurveZ", 1010: "wkbCurvePolygonZ", 1011: "wkbMultiCurveZ",
                 1012: "wkbMultiSurfaceZ", 1013: "wkbCurveZ", 1014: "wkbSurfaceZ",
                 1015: "wkbPolyhedralSurfaceZ", 1016: "wkbTINZ", 1017: "wkbTriangleZ",
                 2001: "wkbPointM", 2002: "wkbLineStringM", 2003: "wkbPolygonM", 2004: "wkbMultiPointM",
                 2005: "wkbMultiLineStringM", 2006: "wkbMultiPolygonM", 2007: "wkbGeometryCollectionM",
                 2008: "wkbCircularStringM", 2009: "wkbCompoundCurveM", 2010: "wkbCurvePolygonM",
                 2011: "wkbMultiCurveM", 2012: "wkbMultiSurfaceM", 2013: "wkbCurveM", 2014: "wkbSurfaceM",
                 2015: "wkbPolyhedralSurfaceM", 2016: "wkbTINM", 2017: "wkbTriangleM", 3001: "wkbPointZM",
                 3002: "wkbLineStringZM", 3003: "wkbPolygonZM", 3004: "wkbMultiPointZM",
                 3005: "wkbMultiLineStringZM", 3006: "wkbMultiPolygonZM", 3007: "wkbGeometryCollectionZM",
                 3008: "wkbCircularStringZM", 3009: "wkbCompoundCurveZM", 3010: "wkbCurvePolygonZM",
                 3011: "wkbMultiCurveZM", 3012: "wkbMultiSurfaceZM", 3013: "wkbCurveZM",
                 3014: "wkbSurfaceZM", 3015: "wkbPolyhedralSurfaceZM", 3016: "wkbTINZM", 3017: "wkbTriangleZM",
                 -2147483647: "wkbPoint25D", -2147483646: "wkbLineString25D", -2147483645: "wkbPolygon25D",
                 -2147483644: "wkbMultiPoint25D", -2147483643: "wkbMultiLineString25D",
                 -2147483642: "wkbMultiPolygon25D", -2147483641: "wkbGeometryCollection25D"}
    try:
        geom_type = layer.GetGeom()
    except AttributeError:
        print("ERROR: Invalid input: %s is empty or not osgeo.ogr.Layer." % str(layer))
        return type_dict[0]
    try:
        return type_dict[geom_type]
    except KeyError:
        print("ERROR: Unknown WKB Geometry Type.")
        return type_dict[0]


def get_geom_simplified(layer):
    """
    Get a simplified geometry description (either point, line, or polygon) as a function of
     the WKB Geometry Type of a shapefile layer
    :param layer: osgeo.ogr.Layer
    :output: STR of either point, line, or polygon (or unknown if invalid layer)
    """
    wkb_geom = get_geom_description(layer)
    if "point" in wkb_geom.lower():
        return "point"
    if "line" in wkb_geom.lower():
        return "line"
    if "polygon" in wkb_geom.lower():
        return "polygon"
    return "unknown"


def verify_shp_name(shp_file_name, shorten_to=13):
    """
    Ensure that the shapefile name does not exceed 13 characters or shorten the shp_file_name length
    to N characters
    :param shp_file_name: STR of a shapefile name (with directory e.g., "C:/temp/poly.shp")
    :param shorten_to: INT of the number of characters the shapefile name should have - default=13
    :output: STR of shapefile name (including path if provided) with a length of shorten_to
    """
    pure_fn = shp_file_name.split(".shp")[0].split("/")[-1].split("\\")[-1]
    shp_dir = shp_file_name.strip(shp_file_name.split("/")[-1].split("\\")[-1])
    if pure_fn.__len__() > shorten_to:
        return shp_dir + pure_fn[0: shorten_to - 1] + ".shp"
    else:
        return shp_file_name
