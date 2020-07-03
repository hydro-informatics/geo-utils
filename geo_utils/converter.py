from raster_mgmt import *
from shp_mgmt import *
import itertools
gdal.UseExceptions()


def coords2offset(geo_transform, x_coord, y_coord):
    """
    Returns x-y pixel offset
    :param geo_transform: osgeo.gdal.Dataset.GetGeoTransform() object
    :param x_coord: FLOAT of x-coordinate
    :param y_coord: FLOAT of y-coordinate
    :return: offset_x, offset_y (both integer of pixel numbers)
    """
    try:
        origin_x = geo_transform[0]
        origin_y = geo_transform[3]
        pixel_width = geo_transform[1]
        pixel_height = geo_transform[5]
    except IndexError:
        print("ERROR: Invalid geo_transform object (%s)." % str(geo_transform))
        return None
    except:
        print("ERROR: Invalid geo_transform object (%s)." % str(geo_transform))
        return None

    try:
        offset_x = int((x_coord - origin_x) / pixel_width)
        offset_y = int((y_coord - origin_y) / pixel_height)
    except ValueError:
        print("ERROR: geo_transform tuple contains non-numeric data: %s" % str(geo_transform))
        return None
    return offset_x, offset_y


def get_layer(dataset, band_number=1):
    """
    Get a layer=band (RasterDataSet) or layer=ogr.Dataset.Layer() of any dataset
    :param dataset: osgeo.gdal.Dataset or osgeo.ogr.DataSource
    :param band_number: ONLY FOR RASTERS - INT of the raster band number to open (default: 1)
    :output: DICT {GEO-TYPE: if raster: raster_band, if vector: GetLayer(), else: None}
    """
    if verify_dataset(dataset) == "raster":
        return {"type": "raster", "layer": dataset.GetRasterBand(band_number)}
    if verify_dataset(dataset) == "vector":
        return {"type": "vector", "layer":  dataset.GetLayer()}
    return {"type": "None", "layer": None}


def raster2line(raster_file_name, out_shp_fn, pixel_value):
    """
    Convert a raster to a line shapefile, where pixel_value determines line start and end points
    :param raster_file_name: STR of input raster file name, including directory; must end on ".tif"
    :param out_shp_fn: STR of target shapefile name, including directory; must end on ".shp"
    :param pixel_value: INT/FLOAT of a pixel value
    :return: None (writes new shapefile).
    """

    # calculate max. distance between points
    # ensures correct neighbourhoods for start and end pts of lines
    raster, array, geo_transform = open_raster(raster_file_name)
    pixel_width = geo_transform[1]
    max_distance = np.ceil(np.sqrt(2 * pixel_width**2))

    # convert raster array to points dict
    count = 0
    trajectory = np.where(array == pixel_value)  # nested list
    pts_dict = {}
    for index_y in trajectory[0]:
        index_x = trajectory[1][count]
        coord_x, coord_y = coords2offset(raster_file_name, index_x, index_y)
        pts_dict[count] = (coord_x, coord_y)
        count += 1

    # create multiline (write points dictionary to line geometry (wkbMultiLineString)
    multi_line = ogr.Geometry(ogr.wkbMultiLineString)
    for i in itertools.combinations(pts_dict.values(), 2):
        point1 = ogr.Geometry(ogr.wkbPoint)
        point1.AddPoint(i[0][0], i[0][1])
        point2 = ogr.Geometry(ogr.wkbPoint)
        point2.AddPoint(i[1][0], i[1][1])

        distance = point1.Distance(point2)

        if distance < max_distance:
            line = ogr.Geometry(ogr.wkbLineString)
            line.AddPoint(i[0][0],i[0][1])
            line.AddPoint(i[1][0],i[1][1])
            multi_line.AddGeometry(line)

    # verify output shapefile name
    out_shp_fn = verify_shp_name(out_shp_fn)

    # write multiline (wkbMultiLineString2shp) to shapefile
    shp_driver = ogr.GetDriverByName("ESRI Shapefile")
    if os.path.exists(out_shp_fn):
        shp_driver.DeleteDataSource(out_shp_fn)
    new_shp = create_shp(out_shp_fn, layer_name="raster_pts", layer_type="line")
    lyr = new_shp.GetLayer()
    feature_def = lyr.GetLayerDefn()
    new_line_feat = ogr.Feature(feature_def)
    new_line_feat.SetGeometry(multi_line)
    lyr.CreateFeature(new_line_feat)
    print("Success: Wrote %s" % str(out_shp_fn))


def raster2polygon(file_name, band_number=1, output_shapefile="", layer_name="basemap"):
    """
    Convert a raster to polygon
    :param file_name: STR of target file name, including directory; must end on ".tif"
    :param band_number: INT of the raster band number to open (default: 1)
    :param output_shapefile: STR of a shapefile name (with directory e.g., "C:/temp/poly.shp")
    :param layer_name: STR of a layer name
    :return: None
    """
    raster, raster_band = open_raster(file_name, band_number=band_number)

    driver = ogr.GetDriverByName("ESRI Shapefile")
    dst_ds = driver.CreateDataSource(output_shapefile)
    dst_layer = dst_ds.CreateLayer(layer_name, srs=None)

    gdal.Polygonize(raster_band, None, dst_layer, -1, [], callback=None)


def verify_dataset(dataset):
    """
    Verify if a dataset contains raster or vector data
    :param dataset: osgeo.gdal.Dataset or osgeo.ogr.DataSource
    :return: String (either "mixed", "raster", or "vector")
    """
    # Check the contents of an osgeo.gdal.Dataset
    try:
        if dataset.RasterCount > 0 and dataset.GetLayerCount() > 0:
            return "mixed"
        elif dataset.RasterCount > 0:
            return "raster"
        elif dataset.GetLayerCount() > 0:
            return "vector"
        else:
            return "empty"
    except AttributeError:
        print("ERROR: %s is not an osgeo.gdal.Dataset object." % str(dataset))