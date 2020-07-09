from srs_mgmt import *
import itertools
gdal.UseExceptions()


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
    raster, array, geo_transform = raster2array(raster_file_name)
    pixel_width = geo_transform[1]
    max_distance = np.ceil(np.sqrt(2 * pixel_width**2))

    # extract pixels with the user-defined pixel value from the raster array
    trajectory = np.where(array == pixel_value)
    if np.count_nonzero(trajectory) is 0:
        print("ERROR: The defined pixel_value (%s) does not occur in the raster band." % str(pixel_value))
        return None

    # convert pixel offset to coordinates and append to nested list of points
    points = []
    count = 0
    for offset_y in trajectory[0]:
        offset_x = trajectory[1][count]
        points.append(offset2coords(geo_transform, offset_x, offset_y))
        count += 1

    # create multiline (write points dictionary to line geometry (wkbMultiLineString)
    multi_line = ogr.Geometry(ogr.wkbMultiLineString)
    for i in itertools.combinations(points, 2):
        point1 = ogr.Geometry(ogr.wkbPoint)
        point1.AddPoint(i[0][0], i[0][1])
        point2 = ogr.Geometry(ogr.wkbPoint)
        point2.AddPoint(i[1][0], i[1][1])

        distance = point1.Distance(point2)
        if distance < max_distance:
            line = ogr.Geometry(ogr.wkbLineString)
            line.AddPoint(i[0][0], i[0][1])
            line.AddPoint(i[1][0], i[1][1])
            multi_line.AddGeometry(line)

    # write multiline (wkbMultiLineString2shp) to shapefile
    new_shp = create_shp(out_shp_fn, layer_name="raster_pts", layer_type="line")
    lyr = new_shp.GetLayer()
    feature_def = lyr.GetLayerDefn()
    new_line_feat = ogr.Feature(feature_def)
    new_line_feat.SetGeometry(multi_line)
    lyr.CreateFeature(new_line_feat)

    # create projection file
    srs = get_srs(raster)
    make_prj(out_shp_fn, int(srs.GetAuthorityCode(None)))
    print("Success: Wrote %s" % str(out_shp_fn))


def raster2polygon(file_name, band_number=1, out_shp_fn="", layer_name="basemap"):
    """
    Convert a raster to polygon
    :param file_name: STR of target file name, including directory; must end on ".tif"
    :param band_number: INT of the raster band number to open (default: 1)
    :param out_shp_fn: STR of a shapefile name (with directory e.g., "C:/temp/poly.shp")
    :param layer_name: STR of a layer name
    :return: None
    """
    raster, raster_band = open_raster(file_name, band_number=band_number)

    # verify output shapefile name
    out_shp_fn = verify_shp_name(out_shp_fn)

    driver = ogr.GetDriverByName("ESRI Shapefile")
    dst_ds = driver.CreateDataSource(out_shp_fn)
    dst_layer = dst_ds.CreateLayer(layer_name, srs=None)

    gdal.Polygonize(raster_band, None, dst_layer, -1, [], callback=None)
    print("Success: Wrote %s" % str(out_shp_fn))


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