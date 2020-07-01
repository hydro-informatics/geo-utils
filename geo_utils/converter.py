from raster_mgmt import *
from shp_mgmt import *

gdal.UseExceptions()


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

    gdal.Polygonize(raster_band, None, dst_layer, -1, [], callback=None )