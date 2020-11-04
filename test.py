from geo_utils.geo_utils import *


# get source file names as list
src_data_dir = "/media/sf_shared/luftbilder_20201030/Inn_20200117_RGB_tiff/"
files = glob.glob("%s*.tif" % src_data_dir)

# read image anchors (origins) from kml file
src_kml = "/media/sf_shared/luftbilder_20201030/Traj_1_InnWWARo_17012020_RGBevents_UniStuttgart.kml"
gdf_kml = kmx2other(src_kml, output="gpd")

print(gdf_kml.dtypes)
print(gdf_kml["coordinates"][5])
print(gdf_kml["description"][5])
print(gdf_kml["styleUrl"][5])
print(gdf_kml["geometry"][5])

# for gg in gdf_kml["geometry"]:
#     print(gg)

# create reference raster
