"""Basic imports for geo_utils"""
try:
    import logging
    import glob
    import os
    import urllib
    import subprocess
    import itertools
except ImportError as e:
    raise ImportError("Could not import standard libraries:\n{0}".format(e))

# import scientific python packages
try:
    import numpy as np
    # import matplotlib  # for future use
except ImportError as e:
    raise ImportError("Could not import numpy/matplotlib (is it installed?). {0}".format(e))
try:
    import pandas as pd
except ImportError as e:
    raise ImportError("Could not import pandas (is it installed?). {0}".format(e))

# import osgeo python packages
try:
    import gdal
    import osr
    from gdal import ogr
except ImportError as e:
    raise ImportError("Could not import gdal and dependent packages (is it installed?). {0}".format(e))

# import other geospatial python packages
try:
    import geopandas
except ImportError as e:
    raise ImportError("Could not import geopandas (is it installed?). {0}".format(e))
try:
    import alphashape
except ImportError as e:
    raise ImportError("Could not import alphashape (is it installed?). {0}".format(e))
try:
    import shapely
    from shapely.geometry import Polygon, LineString, Point
except ImportError as e:
    raise ImportError("Could not import shapely (is it installed?). {0}".format(e))
try:
    import fiona
except ImportError as e:
    raise ImportError("Could not import fiona (is it installed?). {0}".format(e))
try:
    # install pyshp to enable shapefile import
    import shapefile
except ImportError as e:
    raise ImportError("Could not import pyshp (shapefile - is it installed?). {0}".format(e))
try:
    import geojson
except ImportError as e:
    raise ImportError("Could not import fiona (is it installed?). {0}".format(e))


nan_value = -9999.0

gdal_dtype_dict = {
    0: "gdal.GDT_Unknown",
    1: "gdal.GDT_Byte",
    2: "gdal.GDT_UInt16",
    3: "gdal.GDT_Int16",
    4: "gdal.GDT_UInt32",
    5: "gdal.GDT_Int32",
    6: "gdal.GDT_Float32",
    7: "gdal.GDT_Float64",
    8: "gdal.GDT_CInt16",
    9: "gdal.GDT_CInt32",
    10: "gdal.GDT_CFloat32",
    11: "gdal.GDT_CFloat64",
}
