# Geospatial Utility Functions for Hydraulics and Morphodynamics


# Introduction
`geo_utils` provides *Python3* functions for many sorts of river-related analyses with geospatial data. The package is intended as support material for the lecture [*Python programming for Water Resources Engineering and Research*](https://hydro-informatics.github.io/hy_ppwrm.html), where primarily *conda* environments are used. Even though `geo_utils` basically works in all *Python3* environments, make sure to follow the *Get Started* instructions on [hydro-informatics.github.io](https://hydro-informatics.github.io/hy_ide.html) to get ready with *Anaconda* and familiarize with [*git*](https://hydro-informatics.github.io/hy_git.html).


# Installation
Use `git` to download the `geo_utils` repository (make sur to [install Git Bash](https://git-scm.com/downloads)):

1. Open *Git Bash* (or any other git-able *Terminal*)
1. Create or select a target directory for `geo_utils` (e.g., in your *Python* project folder)
1. Type `cd "D:/Target/Directory/"` to change to the target installation directory
1. Clone the repository: `git clone https://github.com/hydro-informatics/geo-utils.git`

# Usage
1. Run *Python* and add the download directory of `geo-utils` to the system path:

```python
import os, sys
sys.path.append("D:/Target/Directory/geo-utils/geo_utils")  # Of course: replace "D:/Target/Directory/", e.g., with  r'' + os.path.abspath('')
```

2. Import `geo_utils`:
```python
import geo_utils as gu
```

### Example

```python
import geo_utils as gu
raster, array, geo_transform = gu.raster2array("/sample-data/froude.tif")
type(raster)
<class 'osgeo.gdal.Dataset'>
type(array)
<class 'numpy.ndarray'>
type(geo_transform)
<class 'tuple'>
print(geo_transform)
(6748604.7742, 3.0, 0.0, 2207317.1771, 0.0, -3.0)
```

# Requirements
 * Python 3.x (read more on [hydro-informatics.github.io](https://hydro-informatics.github.io/hy_ide.html))
 * Fundamental packages: `numpy`, `gdal` (read more on [hydro-informatics.github.io](https://hydro-informatics.github.io/geo-pckg.html#gdal)
 
# Utility Documentation
## Package structure

![structure](https://github.com/hydro-informatics/geo-utils/raw/master/graphs/geo-utils-uml.png)
 
## Files (modules) and descriptions

* `srs_mgmt`: Manage projections and spatial reference systems of raster and vector datasets
* `shp_mgmt`: Create shapefiles (vector data).
* `raster_mgmt`: Open and create raster datasets, and convert raster bands to a *numpy* array.
* `dataset_mgmt`:  Inherits functions from `shp_mgmt` and `raster_mgmt`, and provides universal layer and geospatialization functions. 
* `geo_tools`: Universal functions to convert raster to vector datasets and vice versa.


## Manage shapefiles (vector data)

The methods provided with `shp_mgmt` are: 
* `create_shp` to create a new shapefile (similar to the [course function](https://hydro-informatics.github.io/geo-shp.html#create-a-new-shapefile)).
* `get_geom_description` gets the WKB Geometry Type as string from a shapefile layer.
* `get_geom_simplified` gets a simplified geometry description (either point, line, or polygon) as a function of a WKB Geometry Type of a shapefile layer.
* `verify_shp_name` ensures that a shapefile name does not exceed 13 characters or shortens the shapefile name length to N characters.

### Create shapefile

Usage: `create_shp(shp_file_dir, overwrite=True, **kwargs)`

| Input arguments | Type | Description |
|-----------------|------|-------------|
|`shp_file_dir` | String | Of a (relative) shapefile directory (ends on `".shp"`, e.g., `"C:/temp/poly.shp"`).|
|`overwrite` | Boolean | OPTIONAL parameter - if `True` (=default), existing shapefiles with the same name as `shp_file_dir` are overwritten. |
|`layer_name`| String | OPTIONAL layer name (no layer will be created if the argument is not provided).|
|`layer_type`| String | OPTIONAL layer type may be "point, "line", or "polygon" (no layer will be created if the argument is not provided).|

Output: `osgeo.ogr.DataSource` (*Python* shapefile object)

### Get Geometry Type of a shapefile
Method returns the *WKB* geometry type description of a `osgeo.ogr.Layer.GetGeom()` integer number. <br>
Usage: `get_geom_description(layer)`


| Input arguments | Type | Description |
|-----------------|------|-------------|
|`layer` | osgeo.ogr.Layer | Any layer provided with `osgeo.ogr.DataSource.GetLayer()`.|

Output: String of *WKB* geometry (e.g., `"wkbPoint"`, `"wkbLineString"`, or `"wkbPolygon"`).

### Get simplified Geometry Type of a shapefile for use with `create_shp`
Usage:  `get_geom_simplified(layer)`

| Input arguments | Type | Description |
|-----------------|------|-------------|
|`layer` | osgeo.ogr.Layer | Any layer provided with `osgeo.ogr.DataSource.GetLayer()`.|

Output: String of a simplified geometry  that can be provided as `layer_type` argument in the `create_shp` method (e.g., `"point"`, `"line"`, or `"polygon"`).

### Verify shapefile name
A shapefile name should not be longer than 13 characters in total. This function cuts off too long shapefile names (useful for automatically generated shapefile names in code).<br>
Usage:  `verify_shp_name(shp_file_name, **shorten_to)`

| Input arguments | Type | Description |
|-----------------|------|-------------|
|`shp_file_name` | String | Of a (relative) shapefile directory (ends on `".shp"`, e.g., `"C:/temp/poly.shp"`).|
|`shorten_to` | Integer | OPTIONAL number of characters the shapefile name should have - default=13 (use e.g., if you intend to add a prefix or suffix).|

Output: String of a shapefile name <= 13 characters (e.g., `"C:/temp/0123456789012.shp"`).


## Manage rasters 

The methods provided with `raster_mgmt` are: 
* `create_raster` creates a new raster dataset (similar to the [course function](hydro-informatics.github.io/geo-raster.html#create-and-save-a-raster-from-array)).
* `open_raster` opens an existing raster dataset (similar to the [course function](https://hydro-informatics.github.io/geo-raster.html#open-existing-raster-data)).
* `raster2array` converts a raster band to a *numpy* array. 

### Create raster
Usage: `create_raster(file_name, raster_array, origin=None, epsg=4326, pixel_width=10, pixel_height=10, nan_value=-9999.0, rdtype=gdal.GDT_Float32, geo_info=False)`

| Input arguments | Type | Description |
|-----------------|------|-------------|
|`raster_file_name` | String | Of a (relative) raster directory (ends on `".tif"`, e.g., `"C:/temp/a_grid.tif"`).|
|`raster_array` | numpy.array | Values to rasterize in the form of a *numpy* array.|
|`origin` | Tuple | OPTIONAL, but very recommended to provide an (x, y) origin coordinates - can be superseded with the `geo_info` argument.|
|`epsg` | Integer | OPTIONAL, but very recommended to provide an an [*EPSG* Authority Code](https://hydro-informatics.github.io/geospatial-data.html#prj) - default=4326 |
|`pixel_height` | Integer | OPTIONAL pixel height (multiple of unit defined with the EPSG number) - default=10m - can be superseded with the `geo_info` argument.|
|`pixel_width` | Integer | OPTIONAL pixel width (multiple of unit defined with the EPSG number) - default=10m - can be superseded with the `geo_info` argument.|
|`nan_value` | Integer/Float | OPTIONAL no-data value to be used in the raster (replaces non-numeric and np.nan in array) default=-9999.0 |
|`rdtype` | gdal.GDALDataType | OPTIONAL raster data type - default=gdal.GDT_Float32 (32 bit floating point)|
|`geo_info` | Tuple|  OPTIONAL to define  a gdal.DataSet.GetGeoTransform object (**supersedes origin, pixel_width, pixel_height**) default=False|

Output: None (creates a *GeoTIFF* raster as defined with the `raster_file_name` argument).

### Open raster
Usage: `raster, raster_band = open_raster(file_name, band_number=1)`

| Input arguments | Type | Description |
|-----------------|------|-------------|
|`raster_file_name` | String | Of a (relative) raster directory (ends on `".tif"`, e.g., `"C:/temp/a_grid.tif"`).|
|`band_number`| Integer | OPTIONAL to indicate the raster band number to open (default: 1).|

Output: osgeo.gdal.Dataset, osgeo.gdal.Band objects

### Raster to *numpy* array

Usage: `raster_dataset, array, geo_transformation = raster2array(file_name, band_number=1)`

| Input arguments | Type | Description |
|-----------------|------|-------------|
|`raster_file_name` | String | Of a (relative) raster directory (ends on `".tif"`, e.g., `"C:/temp/a_grid.tif"`).|
|`band_number`| Integer | OPTIONAL to indicate the raster band number to open (default: 1).|

Output: osgeo.gdal.Dataset, numpy.ndarray, tuple (`osgeo.gdal.Dataset.GetGeoTransform()`, i.e., `(x_origin (top left), pixel_width (west-east), 0, y_origin(top left), 0, pixel_height(north-south))` ).

## Projection and spatial reference management
The methods provided with `srs_mgmt` are: 
* `get_wkt` gets a [*WKT*-formatted projection](https://hydro-informatics.github.io/geo-shp.html#prj-shp) of an [*EPSG* Authority Code](https://hydro-informatics.github.io/geospatial-data.html#prj) using the `osr` library.
* `get_esri_wkt` is an online version of `get_wkt` that retrieves *WKT* data from [spatialreference.org](http://spatialreference.org/).
* `get_srs` returns the spatial reference of any raster or vector dataset.
* `make_prj` generates projection files for *Esri* shapefile format. 
* `reproject` (including `reproject_raster` and `reproject_shapefile`) re-projects any raster or vector dataset to the projection and spatial reference system of another raster or vector dataset.

### Get *WKT* formatted projections (`get_wkt`)

Retrieve a [*WKT*-formatted projection](https://hydro-informatics.github.io/geo-shp.html#prj-shp) string of an [*EPSG* Authority Code](https://hydro-informatics.github.io/geospatial-data.html#prj) code using the `osr` library with <br>
`gu.get_wkt(epsg, wkt_format)`

| Input arguments | Type | Description |
|-----------------|------|-------------|
| `epsg` | Integer | [*EPSG* Authority Code](https://hydro-informatics.github.io/geospatial-data.html#prj)|
| `wkt_format` | String | OPTIONAL argument to specify the *WKT* output format; the default is `"esriwkt"` for shapefile projection files.s |

Output: String containing a *WKT* projection, for example: 
```
"GEOGCS["GCS_WGS_1984",
        DATUM["WGS_1984",
            SPHEROID["WGS_84",6378137.0,298.257223563]],
        PRIMEM["Greenwich",0.0],
        UNIT["Degree",0.0174532925199433]]"
```

### Get *ESRI WKT*-formatted projections remotely (`get_esriwkt`)

Retrieve a [*WKT*-formatted projection](https://hydro-informatics.github.io/geo-shp.html#prj-shp) string of an [*EPSG* Authority Code](https://hydro-informatics.github.io/geospatial-data.html#prj) code using the `osr` library with <br>
`gu.get_esriwkt(epsg)`

| Input arguments | Type | Description |
|-----------------|------|-------------|
| `epsg` | Integer | [*EPSG* Authority Code](https://hydro-informatics.github.io/geospatial-data.html#prj)|

Output: String containing a *WKT* projection (see example above).

### Get spatial reference system of any dataset (`get_srs`)
Get the spatial reference of any `gdal.Dataset` with <br>
`gu.get_srs(dataset)`

| Input arguments | Type | Description |
|-----------------|------|-------------|
| `dataset` | gdal.Dataset | Any raster (`gdal.Open(file_name)`) or vector (`ogr_driver.Open(file_name)`) dataset loaded in *Python.|

Output: `osgeo.osr.SpatialReference`

### Make a .prj projection file for an Esri shapefile (`make_prj`)
Create a [`.prj` file](https://hydro-informatics.github.io/geo-shp.html#prj-shp) for an Esri shapefile. The projection information may be generated with the `get_wkt` or `get_esriwkt` functions. Usage:<br>
`make_prj(shp_file_name, epsg`

| Input arguments | Type | Description |
|-----------------|------|-------------|
| `shp_file_name` | String | Shapefile name (with directory e.g., `"C:/temp/poly.shp"`).|
| `epsg` | Integer | [*EPSG* Authority Code](https://hydro-informatics.github.io/geospatial-data.html#prj)|

Output: None.

### Re-project any gdal.Dataset (`reproject`)
Re-project any raster or vector dataset to the projection and spatial reference system of another raster or vector dataset. Usage:<br>
`reproject(source_dataset, new_projection_dataset)`

| Input arguments | Type | Description |
|-----------------|------|-------------|
|`source_dataset` | gdal.Dataset | Shapefile or raster to re-project.|
|`new_projection_dataset`| gdal.Dataset | A shapefile or raster containing the target projection.|

Output: None (creates a new shapefile or raster in the directory of the `source_dataset`).


## Dataset management (general functions for raster and vector datasets) 

The methods provided with `dataset_mgmt` are: 
* `coords2offset` converts x-y coordinates to a pixel offset relative to the origin of the spatial reference used.
* `get_layer` gets a layer of any dataset (raster or vector); if raster(osgeo.gdal.Dataset): layer=osgeo.gdal.Band; if vector (osgeo.ogr.DataSource): layer=osgeo.ogr.Layer' (useful for automation and data verification).
* `offset2coords` is the inverse function of `coords2offset` and converts x-y pixel offset to x-y coordinates to relative to the origin of the spatial reference used.
* `verify_dataset` checks if a dataset is vector, raster, or mixed.
* `raster2line` converts a raster to a line vector dataset based on a user-specific value of pixels to connect. 
* `raster2polygon` converts a raster to a polygon vector dataset. 

### Get pixel offset from x-y coordinates and vice versa
Convert x-y coordinates to a pixel offset, and vice verse, relative to the origin of the spatial reference (defined with `geo_transform`) used.<br>
Usage (coordinates to offset): `offset_x, offset_y = coords2offset(geo_transform, x_coord, y_coord)`
Usage (offset to coordinates): `x_coord, y_coord = offset2oords(geo_transform, offset_x, offset_y)`

| Input arguments | Type | Description |
|-----------------|------|-------------|
|`geo_transform` | Tuple|  Defined by a gdal.DataSet.GetGeoTransform object.|
|`x_coord`| Float | x-value of a pixel or point.|
|`y_coord`| Float | y-value of a pixel or point.|

Output: offset_x, offset_y (both integer of pixel numbers) or x_coord, y_coord (both float coordinates). 


### Get layer and dataset type info
Usage: `get_layer(dataset, band_number=1)`

| Input arguments | Type | Description |
|-----------------|------|-------------|
| `dataset` | osgeo.gdal.Dataset or osgeo.ogr.DataSource | Raster or vector dataset to verify.|
|`band_number`| Integer | OPTIONAL to indicate the raster band number to open (default: 1).|

Output: Dictionary of `{"type": "raster" or "vector", "layer": osgeo.gdal.Band (if raster)  or osgeo.ogr.Layer (if vector)}` (application example: `srs_mgmt.reproject(DATASET, DATASET)`). 

### Verify dataset type info
Usage: `verify_dataset(dataset)`

| Input arguments | Type | Description |
|-----------------|------|-------------|
| `dataset` | osgeo.gdal.Dataset or osgeo.ogr.DataSource | Raster or vector dataset to verify.|

Output: String (either `"mixed"`, `"raster"`, or `"vector"`). 

## Dataset conversion

Convert rasters to shapefiles and vice versa. 

The methods provided with `geo_tools` are: 
* `float2int` converts a float to an integer type raster dataset. 
* `raster2line` converts a raster to a line vector dataset based on a user-specific value of pixels to connect. 
* `raster2polygon` converts a raster to a polygon vector dataset.
* `points2raster` converts a points or a point shapefile to raster dataset. 
* `polygon2raster` converts a polygon shapefile to a raster dataset.  

### Convert float to integer raster dataset
Convert a floating point raster data to integers with `numpy.array.astype(int)`.<br>
Usage: `int_raster_file_name = float2int(raster_file_name, band_number)`

| Input arguments | Type | Description |
|-----------------|------|-------------|
|`raster_file_name` | String | Of a (relative) directory (ends on `".tif"`, e.g., `"C:/temp/a_grid.tif"`) of raster with pixel data types only.|
|`band_number`| Integer | OPTIONAL to indicate the raster band number to open (default: 1).|

Output: *String* of the integer raster file name (i.e., a raster with an `_int.tif` suffix is created in the same directory and with the same raster file name prefix as `raster_file_name`). For example: `"C:/rasters/flow_depth_int.tif"`.

### Convert raster to line shapefile
Convert a raster to a line shapefile based on a user-specific value of pixels (`pixel_value`) to connect.<br>
Usage: `raster2line(raster_file_name, out_shp_fn, pixel_value)`

| Input arguments | Type | Description |
|-----------------|------|-------------|
|`raster_file_name` | String | Of a (relative) directory (ends on `".tif"`, e.g., `"C:/temp/a_grid.tif"`) of raster with pixel data types only.|
|`out_shp_fn` | String | Output shapefile name (with directory e.g., `"C:/temp/poly.shp"`).|
|`pixel_value` | Integer or Float | Pixel value to select pixels to connect with lines.|

Output: None (produces a line shapefile based on a `wkbMultiLineString`, with the name define in the `out_shp_fn` argument).

### Convert raster to polygon shapefile

Usage: `raster2polygon(file_name, band_number=1, out_shp_fn="", layer_name="basemap")`

| Input arguments | Type | Description |
|-----------------|------|-------------|
|`raster_file_name` | String | Of a (relative) directory (ends on `".tif"`, e.g., `"C:/temp/a_grid.tif"`) of raster with **INTEGER** pixel data types only. If *Float* data is provided, the function automatically uses `float2int`.|
|`band_number`| Integer | OPTIONAL to indicate the raster band number to open (default: 1).|
|`out_shp_fn` | String | shapefile name (with directory e.g., `"C:/temp/poly.shp"`).|
|`field_name` | String | Name for the field where the values of the raster are stored (default=`"values"`).|

Output: None (produces a polygon shapefile with `gdal.Polygonize`, with the name define in the `out_shp_fn` argument).

### Rasterize
Convert any shapefile to a raster by burning values of its features to a raster.

Usage: `rasterize(n_shp_file_name, out_raster_file_name, pixel_size=10, no_data_value=-9999, rdtype=gdal.GDT_Float32, **kwargs)`

| Input arguments | Type | Description |
|-----------------|------|-------------|
|`in_shp_file_name` | String | Input shapefile name (with directory e.g., `"C:/temp/poly.shp"`).|
|`out_raster_file_name` | String | Of a (relative) directory (ends on `".tif"`, e.g., `"C:/temp/a_grid.tif"`) of a raster to be created.|
|`pixel_size`| Integer | OPTIONAL to indicate the pixel size of the target raster (default: 10).|
|`no_data_value` | Integer | OPTIONAL no data value to be used for pixels that do not contain data (default: -9999).|
|`rdtype` | gdal.GDALDataType | OPTIONAL raster data type (default: gdal.GDT_Float32 - i.e., 32 bit floating point)|
|`field_name` | String | OPTIONAL KEYWORD to indicate the field name of values to be burned to the raster (highly recommended to provide a field name according to the shapefile's attribute table).|

### Points/Polygon to raster
To be implemented...


