# default config ----
# This config is called by default; otherwise the user normally specifies
# a config .yaml file.
# Stored in source for now, perhaps we don't need to do anything more since
# it isn't data and it's a small list.
# NOTE 2022-06-04: Team is updating config to use widgets and adding more options to the file, will need to update at some point.
default_config <-
  list(
    inpath = "/input",
    infname = "input/Pointdata_Llara.csv",
    colname_lng = "Long",
    colname_lat = "Lat",
    outpath = "data/",
    target_bbox = "None",
    target_res = "None",
    target_crs = "EPSG:4326",
    target_dates = "2009",
    target_aggregation = "year", target_sources = list(
      SLGA = list(
        names = c("Organic_Carbon", "Clay", "Depth_of_Soil"),
        agfunctions = c("mean", "mean", "mean")
      ), SILO = list(
        names = c(
          "monthly_rain", "max_temp", "min_temp",
          "evap_pan"
        ), agfunctions = c(
          "sum", "mean", "mean",
          "sum"
        )
      ), DEA = list(
        names = "landsat8_nbart_16day",
        agfunctions = c("mean", "perc95", "perc5")
      ), DEM = list(
        names = "DEM_1s"
      )
    )
  )
