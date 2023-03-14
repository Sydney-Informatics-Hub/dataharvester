# Some example test functions
# Restart session first

library(devtools)
#load_all('./dataharvester')

# Initialise harvester with eearth engine
initialise_harvester("r-harvester", earthengine= TRUE)

tempDir <- "harvester_test"
dir.create(tempDir)

outfiles_rad <- download_radiometric(
  layer = 'radmap2019_grid_dose_terr_awags_rad_2019',
  bounding_box = c(149.769345, -30.335861, 149.949173, -30.206271),
  outpath = tempDir,
  resolution = 6)

outfile_slga <- download_slga(
  layernames = "Bulk_Density",
  bounding_box = c(149.769345, -30.335861, 149.949173, -30.206271),
  out_path = tempDir,
  resolution = 6,
  depth_min = 0,
  depth_max = 5
)

outfiles_slga <- download_slga(
  layernames = list("Bulk_Density","Clay"),
  bounding_box = c(149.769345, -30.335861, 149.949173, -30.206271),
  out_path = tempDir,
  resolution = 6,
  depth_min = c(0,0),
  depth_max = c(5,5)
)

outfiles_dea <- download_dea(
  layernames = list("landsat_barest_earth","ga_ls_ard_3"),
  bounding_box = c(149.769345, -30.335861, 149.949173, -30.206271),
  out_path = tempDir,
  resolution = 6,
  date_min = "2022-10-01",
  date_max = "2022-11-01",
)

outfiles_silo <- download_silo(
  layernames = list("max_temp","min_temp"),
  bounding_box = c(149.769345, -30.335861, 149.949173, -30.206271),
  out_path = tempDir,
  date_min = "2022-10-01",
  date_max = "2022-11-01",
)

outfile_landscape <- download_landscape(
  layernames = "Slope",
  bounding_box = c(149.769345, -30.335861, 149.949173, -30.206271),
  out_path = tempDir,
  resolution = 6
)

outfiles_landscape <- download_landscape(
  layernames = list("Slope","Aspect"),
  bounding_box = c(149.769345, -30.335861, 149.949173, -30.206271),
  out_path = tempDir,
  resolution = 6
)


outfile_dem <- download_dem(
  layernames = "DEM",
  bounding_box = c(149.769345, -30.335861, 149.949173, -30.206271),
  out_path = tempDir,
  resolution = 6
)

# Test all download function at once
path_to_config = "dataharvester/data/settings_harvest.yaml"
harvest(path_to_config, plot = TRUE)

# Test only GEE
path_to_config = "dataharvester/data/settings_harvest_gee.yaml"
img = auto_ee(path_to_config)

