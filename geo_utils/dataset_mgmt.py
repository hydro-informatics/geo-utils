from raster_mgmt import *
from shp_mgmt import *
gdal.UseExceptions()


def coords2offset(geo_transform, x_coord, y_coord):
    """
    Returns x-y pixel offset (inverse of offset2coords function)
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


def offset2coords(geo_transform, offset_x, offset_y):
    """
    Returns x-y coordinates from pixel offset (inverse of coords2offset function)
    :param geo_transform: osgeo.gdal.Dataset.GetGeoTransform() object
    :param offset_x: integer of x pixel numbers
    :param offset_y: integer of y pixel numbers
    :return: x_coord, y_coord (FLOATs of x-y-coordinates)
    """
    try:
        origin_x = geo_transform[0]
        origin_y = geo_transform[3]
        pixel_width = geo_transform[1]
        pixel_height = geo_transform[5]
    except IndexError:
        print("ERROR: Invalid geo_transform object (%s)." % str(geo_transform))
        return None

    try:
        coord_x = origin_x + pixel_width * (offset_x + 0.5)
        coord_y = origin_y + pixel_height * (offset_y + 0.5)
    except ValueError:
        print("ERROR: geo_transform tuple contains non-numeric data: %s" % str(geo_transform))
        return None
    return coord_x, coord_y


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
    except AttributeErrorimport gdal
import osr
from config import *


def open_raster(file_name, band_number=1):
    """
    Open a raster file and access its bands
    :param file_name: STR of a raster file directory and name
    :param band_number: INT of the raster band number to open (default: 1)
    :output: osgeo.gdal.Dataset, osgeo.gdal.Band objects
    """
    gdal.UseExceptions()
    # open raster file or return None if not accessible
    try:
        raster = gdal.Open(file_name)
    except RuntimeError as e:
        print("ERROR: Cannot open raster.")
        print(e)
        return nan_value, nan_value
    # open raster band or return None if corrupted
    try:
        raster_band = raster.GetRasterBand(band_number)
    except RuntimeError as e:
        print("ERROR: Cannot access raster band.")
        print(e)
        return raster, nan_value
    return raster, raster_band


def create_raster(file_name, raster_array, origin=None, epsg=4326, pixel_width=10, pixel_height=10,
                  nan_value=-9999.0, rdtype=gdal.GDT_Float32, geo_info=False):
    """
    Convert a numpy.array to a GeoTIFF raster with the following parameters
    :param file_name: STR of target file name, including directory; must end on ".tif"
    :param raster_array: np.array of values to rasterize
    :param origin: TUPLE of (x, y) origin coordinates
    :param epsg: INT of EPSG:XXXX projection to use - default=4326
    :param pixel_height: INT of pixel height (multiple of unit defined with the EPSG number) - default=10m
    :param pixel_width: INT of pixel width (multiple of unit defined with the EPSG number) - default=10m
    :param nan_value: INT/FLOAT no-data value to be used in the raster (replaces non-numeric and np.nan in array)
                        default=-9999.0
    :param rdtype: gdal.GDALDataType raster data type - default=gdal.GDT_Float32 (32 bit floating point)
    :param geo_info: TUPLE defining a gdal.DataSet.GetGeoTransform object (supersedes origin, pixel_width, pixel_height)
                        default=False
    :return new_raster: osgeo.gdal.Dataset (uses GTiff driver)
    """
    gdal.UseExceptions()
    # check out driver
    driver = gdal.GetDriverByName("GTiff")

    # create raster dataset with number of cols and rows of the input array
    cols = raster_array.shape[1]
    rows = raster_array.shape[0]
    try:
        new_raster = driver.Create(file_name, cols, rows, 1, eType=rdtype)
    except RuntimeError as e:
        print("ERROR: Could not create %s." % str(file_name))
        return -1
    # replace np.nan values
    raster_array[np.isnan(raster_array)] = nan_value

    # apply geo-origin and pixel dimensions
    if not geo_info:
        try:
            origin_x = origin[0]
            origin_y = origin[1]
        except IndexError:
            print("ERROR: Wrong origin format (required: (INT, INT) - provided: %s)." % str(origin))
            return -1
        try:
            new_raster.SetGeoTransform((origin_x, pixel_width, 0, origin_y, 0, pixel_height))
        except RuntimeError as e:
            print("ERROR: Invalid origin (must be INT) or pixel_height/pixel_width (must be INT) provided.")
            return -1
    else:
        try:
            new_raster.SetGeoTransform(geo_info)
        except RuntimeError as e:
            print(e)
            return -1

    # retrieve band number 1
    band = new_raster.GetRasterBand(1)
    band.WriteArray(raster_array)

    # create projection and assign to raster
    srs = osr.SpatialReference()
    try:
        srs.ImportFromEPSG(epsg)
    except RuntimeError as e:
        print(e)
        return -1
    new_raster.SetProjection(srs.ExportToWkt())

    # release raster band
    band.FlushCache()
    return new_raster


def raster2array(file_name, band_number=1):
    """
    :param file_name: STR of target file name, including directory; must end on ".tif"
    :param band_number: INT of the raster band number to open (default: 1)
    :output: (1) ndarray() of the indicated raster band, where no-data values are replaced with np.nan
             (2) the GeoTransformation used in the original raster
    """
    # open the raster and band (see above)
    raster, band = open_raster(file_name, band_number=band_number)
    try:
        # read array data from band
        band_array = band.ReadAsArray()
    except AttributeError:
        print("ERROR: Could not read array of raster band type=%s." % str(type(band)))
        return raster, band, nan_value
    try:
        # overwrite NoDataValues with np.nan
        band_array = np.where(band_array == band.GetNoDataValue(), np.nan, band_array)
    except AttributeError:
        print("ERROR: Could not get NoDataValue of raster band type=%s." % str(type(band)))
        return raster, band, nan_value
    # return the array and GeoTransformation used in the original raster
    return raster, band_array, raster.GetGeoTransform()


def clip_raster(polygon, in_raster, out_raster):
    """
    :param polygon: polygon filename, including directory; must end on ".shp"
    :param in_raster: raster to be clipped, including directory.
    :param out_raster: target raster, including directory.
    :output: saves raster on the selected dir
    """
    gdal.Warp(out_raster, in_raster, cutlineDSName=polygon)

        pass

    try:
        if dataset.RasterCount > 0:
            return "raster"
    except AttributeError:
        pass

    try:
        if dataset.GetLayerCount() > 0:
            return "vector"
        else:
            return "empty"
    except AttributeError:
        print("ERROR: %s is not an osgeo.gdal.Dataset object." % str(dataset))
        return None
