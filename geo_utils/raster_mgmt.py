import gdal
import osr
import numpy as np


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
        return None
    # open raster band or return None if corrupted
    try:
        raster_band = raster.GetRasterBand(band_number)
    except RuntimeError as e:
        print("ERROR: Cannot access raster band.")
        print(e)
        return None
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
        return None
    # replace np.nan values
    raster_array = np.where(raster_array == raster_array.min(), nan_value, raster_array)

    # apply geo-origin and pixel dimensions
    if not geo_info:
        try:
            origin_x = origin[0]
            origin_y = origin[1]
        except IndexError:
            print("ERROR: Wrong origin format (required: (INT, INT) - provided: %s)." % str(origin))
            return None
        try:
            new_raster.SetGeoTransform((origin_x, pixel_width, 0, origin_y, 0, pixel_height))
        except RuntimeError as e:
            print("ERROR: Invalid origin (must be INT) or pixel_height/pixel_width (must be INT) provided.")
            return None
    else:
        try:
            new_raster.SetGeoTransform(geo_info)
        except RuntimeError as e:
            print(e)
            return None

    # retrieve band number 1
    band = new_raster.GetRasterBand(1)
    band.WriteArray(raster_array)

    # create projection and assign to raster
    srs = osr.SpatialReference()
    try:
        srs.ImportFromEPSG(epsg)
    except RuntimeError as e:
        print(e)
        return None
    new_raster.SetProjection(srs.ExportToWkt())

    # release raster band
    band.FlushCache()


def raster2array(file_name, band_number=1):
    """
    :param file_name: STR of target file name, including directory; must end on ".tif"
    :param band_number: INT of the raster band number to open (default: 1)
    :output: (1) ndarray() of the indicated raster band, where no-data values are replaced with np.nan
             (2) the GeoTransformation used in the original raster
    """
    # open the raster and band (see above)
    raster = gdal.Open(file_name)
    band = raster.GetRasterBand(band_number)
    # read array data from band
    band_array = band.ReadAsArray()
    # overwrite NoDataValues with np.nan
    band_array = np.where(band_array == band.GetNoDataValue(), np.nan, band_array)
    # return the array and GeoTransformation used in the original raster
    return band_array, raster.GetGeoTransform()
