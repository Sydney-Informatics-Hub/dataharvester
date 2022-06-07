#' Load a configuration file for data harvester
#'
#' This function performs a sequence of checks to read a `.yaml` configuration
#' file for the data harvester.
#'
#' First, if no file name or file path is provided, it will load a template
#' configuration.
#'
#' If only a config name is provided (without paths or extension), it will
#' search folders relative to the working folder for a file with the same name,
#' including common folders such as "data" and "config". Where multiple files
#' are found, the user can choose the right file to load by specifying it using
#' the argument `pick`.
#'
#' If a file path is provided, it will load the file from the path.
#'
#' @param x `chr` name of a config file (no .extenson), or path to ".yaml"
#'   config file. If NULL, loads a default config file used as a template to
#'   demonstrate the use of the data harvester.
#' @param pick `int` where more than one config file is found, this argument can
#'   be used to select a specific file. Otherwise, the first file found is used.
#'
#' @return `list; harvester` a list object with additional class of "harvester".
#'   This list stores configuration options for the data harvester.
#' @export
#'
#' @examples
#' load_config() # loads template config as a start
load_config <- function(x = NULL, pick = 1) {

  # If x is NULL, load default; note: this folder might change in the future if
  # we create an R package
  if (is.null(x)) {
    # current default (will change in the future)
    config <- default_config
    cat("Default config loaded\n")
  }

  # Otherwise, check if x points to a yaml file in the following folders:
  # - working folder, or 'settings' or 'config' folder in working folder
  # - previous folder, or 'settings' or 'config' folder in previous folder
  check_folders <- c("", "settings/", "config/", "../",
                     "../settings/", "../config")
  full_paths <- paste0(check_folders, x, ".yaml")
  # generate valid file paths
  valid_paths <- full_paths[which(file.exists(full_paths))]

  if (!is.null(x) & length(valid_paths) == 0) {
    # first check if file path is valid!
    if (file.exists(x)) {
      config <- read_yaml(x)
      cat("Config imported from", x, "\n")
    } else stop("Config file does not exist, please check name or path")
  } else if (length(valid_paths) == 1) {
    config <- read_yaml(valid_paths)
    cat("Config imported from", valid_path, "\n")
  } else if (length(valid_paths) > 1) {
    config <- read_yaml(valid_paths[pick])
    cat("More than one config .yaml found. \n",
        "Loaded [1] ", valid_paths[1],
        ". Use `which` argument to select a different file:", "\n", sep = "")
    cat(sapply(1:length(valid_paths), function(i) {
      paste0("[", i, "] ", valid_paths[i])
    }), "\n")
  }
  class(config) <- append(class(config), "harvester")
  return(invisible(config))
}





#' Configure paths to input and output folders and files
#'
#' This function changes the values for `inpath`, `outpath` and `infname` in the
#' data harvester configuration.
#'
#' @param x `harvester` must be an object of this class, which can be created
#'   using `load_config()`.
#' @param input `chr` path to folder containing input files used to determine
#'   coordinates and other features to download. If `NULL`, does nothing.
#' @param output `chr` path to folder to save results. Images, data frames and
#'   other geospatial data outputs are saved it this folder for easy access. If
#'   `NULL`, does nothing.
#' @param in_file `chr` path to specific file used to determine coordinates and
#'   other features to download. If `NULL`, does nothing.
#'
#' @return `list; harvester` a list object with additional class of "harvester".
#'   This list stores configuration options for the data harvester.
#' @export
#'
#' @examples
#' # load template config, then change paths
#' load_config() %>%
#'   config_paths(input = "../..testdata", output =  "data/")
config_paths <- function(x, input = NULL, output = NULL, in_file = NULL) {

  # Reject if not class 'harvester'
  is_cl_harvester(x)

  # Make changes to input folder, input file or output folder(s)
  if (!is.null(input)) {
    before <- x$inpath
    x$inpath <- input
    cat("***             inpath --> ", input, "\n", sep = "")
  }
  if (!is.null(output)) {
    before <- x$outpath
    x$outpath <- output
    cat("***            outpath --> ", output, "\n", sep = "")
  }
  if (!is.null(in_file)) {
    before <- x$infname
    x$infname <- in_file
    cat("***            infname --> ", in_file, "\n", sep = "")
  }
  return(invisible(x))
}




#' Specify the column names of x and y variables in data file
#'
#' For the data harvester to work, it needs coordinate data. Different users
#' will call these x and y coordinates under different names in their data file
#' e.g. `"Lon"`, `"Long"`, `"x"`, `"Easting"` or `"East"`.
#'
#' Changing  allows the data harvester to identify the x and y coordinates
#' appropriately with the user's help. The values are saved to the options
#' `colname_lng` and `colname_lat` in the data harvester configuration.
#'
#' @param x `harvester` must be an object of this class, which can be created
#'   using `load_config()`.
#' @param xvar `chr` column name of x coordinate stored in input data file, will
#'   replace value in `colname_lng`.
#' @param yvar `chr` column name of y coordinate stored in input data file, will
#'   replace value in `colname_lat`.
#'
#' @return `list; harvester` a list object with additional class of "harvester".
#'   This list stores configuration options for the data harvester.
#' @export
#'
#' @examples
#' #' # load template config, then select references to coordinate columns
#' load_config() %>%
#'   config_xy_names("Long", "Lat")
config_xy_names <- function(x, xvar = NULL, yvar = NULL) {

  # Reject if not class 'harvester'
  is_cl_harvester(x)

  # Change xvar if not NULL
  if (!is.null(xvar) & is.character(xvar)) {
    before <- x$colname_lng
    x$colname_lng <- xvar
    cat("***        colname_lng --> ", xvar, "\n", sep = "")
  }
  # Change yvar if not NULL
  if (!is.null(yvar) & is.character(yvar)) {
    before <- x$colname_lat
    x$colname_lat <- yvar
    cat("***        colname_lat --> ", yvar, "\n", sep = "")
  }
  return(invisible(x))
}






#' Specify bounding box limits as a vector
#'
#' Define the bounding box for the data collected. Normally rectangular, since
#' it is simple/useful for plotting.
#'
#' For EPSG:4326 the bounding box is defined by (long_left, lat_bottom,
#' long_right, lat_top).
#'
#' If projected coordinate reference system is used, the bounding box is defined
#' by: (easting_left, northing_bottom, easting_right, northing_top)
#'
#' If `NULL`, the bounding box will be set at a default min/max of point data
#' +/- 0.05 deg (180 arcsec). arcsec). Also note that if an invalid vector is
#' provided i.e. not containing 4 values, the default bounding box will apply.
#'
#' @param x `harvester` must be an object of this class, which can be created
#'   using `load_config()`
#' @param boundaries `num` a vector of 4 numerical values representing the left,
#'   bottom, right and top coordinates.
#'
#' @return `list; harvester` a list object with additional class of "harvester".
#'   This list stores configuration options for the data harvester.
#' @export
#'
#' @examples
config_bbox <- function(x, boundaries = NULL) {

  # Reject if not class 'harvester'
  is_cl_harvester(x)

  # Check that 4 values are provided as a vector
  if (!is.null(boundaries) & length(boundaries) != 4) {
    cat("Note: bounding box provided is not a vector of 4 numeric values\n")
    boundaries <- NULL
  }
  # Configure bounding box value
  if (is.null(boundaries)) {
    cat("***        target_bbox --> default\n")
  } else {
    x$target_bbox <- boundaries
    cat("***        target_bbox --> ", boundaries, "\n")
  }
  return(invisible(x))
}





#' Define resolution in arcsecs
#'
#' @param x
#' @param value
#'
#' @return
#' @export
#'
#' @examples
config_res <- function(x, value = NULL) {

  # Reject if not class 'harvester'
  is_cl_harvester(x)

  if (!is.null(value) & !is.numeric(value)) {
    cat("Note: resolution must be numeric, switching to default for `target_res`\n")
    value <- NULL
  }

  # Configure resolution value
  if (is.null(value)) {
    x$target_res <- value
    cat("***         target_res --> default\n")
  }
  return(invisible(x))
}





#' Define coordinate reference system
#'
#' @param x
#' @param target_crs
#'
#' @return
#' @export
#'
#' @examples
config_crs <- function(x, target_crs = "EPSG:4326") {

  # Reject if not class 'harvester'
  is_cl_harvester(x)

  # Back to default if not character
  if (!is.character(target_crs)) {
    cat("Note: rarget CRS not recognised, using default EPSG:4326\n")
    new_crs <- "EPSG:4326"
  } else {
    new_crs <- target_crs
  }

  # configure crs
  x$target_crs <- new_crs
  cat("***         target_crs --> ", new_crs, "\n", sep = "")
  return(invisible(x))
}






#' Define download date and times, and summary interval
#'
#' @param x
#' @param dates
#' @param interval
#'
#' @return
#' @export
#'
#' @examples
config_dates <- function(x, dates = NULL, interval = "year") {

  # Reject if not class 'harvester'
  is_cl_harvester(x)

  # DATES
  # TODO: checks for YMD. For now, just check year
  # dates = as.character(dates)

  # Process
  # 1. If dates == NULL | config has date, use config date
  # 2. If dates == NULL | config does not have date, use today
  # 3. If dates has more than a number, use the first one
  # 4. If dates has a number, use it
  if (is.null(dates) & length(x$target_dates) == 1) {
    selected_date <- x$target_dates
  } else if (is.null(dates) & length(x$target_dates) < 1) {
    selected_date <- as.character(format(Sys.Date(), "%Y"))
  } else if (length(dates) > 1) {
    selected_date <- as.character(dates[1])
    cat("More than 1 date provided,",
        "will select first date for now...\n")
  } else if (length(dates) == 1) {
    selected_date <- as.character(dates)
  }
  x$target_dates <- selected_date
  cat("***       target_dates --> ",
      selected_date, "\n", sep = "")

  # INTERVAL
  if (interval %in% c("year", "month", "day")) {
    x$target_aggregation <- interval
    cat("*** target_aggregation --> ", interval, "\n", sep = "")
  } else {
    cat("Data summary interval not recgonised. Using default year'\n")
  }


  return(invisible(x))
}





#' Configure SLGA resource download settings
#'
#' @param x
#' @param layers
#' @param summaries
#'
#' @return
#' @export
#'
#' @examples
config_slga <- function(x, layers = NULL, summaries = "mean") {

  # Reject if not class 'harvester'
  is_cl_harvester(x)

  # Process layers if provided, and warn if a layer is not recognised
  if (!is.null(layers)) {
    layers <- is_valid_source("slga", layers)
  } else {
    layers <- x$target_sources$SLGA$names
  }

  # If only one summary is provided, assume it's for all layers
  if (length(summaries) == 1) {
    summaries <- rep(summaries, length(layers))
  }
  # Warn if length of summaries is not equal to length of layers
  if (length(summaries) < length(layers)) {
    warning("SLGA: `length()` of layers must match `length()` of summaries. Downloads might fail.")
  }

  # Apply settings
  if (!is.null(layers)) x$target_sources$SLGA$names <- layers
  cat(
    "***        SLGA layers -->",
    paste0('"', paste(layers, collapse = '", "'), '"'), "\n"
  )
  x$target_sources$SLGA$agfunctions <- summaries
  cat(
    "***         SLGA stats -->",
    paste0('"', paste(summaries, collapse = '", "'), '"'), "\n"
  )
  return(invisible(x))
}



#' Configure SILO resource download settings
#'
#' @param x
#' @param layers
#' @param summaries
#'
#' @return
#' @export
#'
#' @examples
config_silo <- function(x, layers = NULL, summaries = NULL) {

  # Reject if not class 'harvester'
  is_cl_harvester(x)
  # Process layers, and warn if a layer is not recognised
  layers <- is_valid_source("silo", layers)
  # TODO: warn if summaries not recognised
  # If only one summary is provided, assume it's for all layers
  if (length(summaries) == 1) {
    summaries <- rep(summaries, length(layers))
  }
  # Warn if length of summaries is not equal to length of layers
  if (length(summaries) < length(layers)) {
    warning("SILO: `length()` of layers must match `length()` of summaries. Downloads might fail.")
  }

  # Apply settings
  x$target_sources$SILO$names <- layers
  cat(
    "***        SILO layers -->",
    paste0('"', paste(layers, collapse = '", "'), '"'), "\n"
  )
  x$target_sources$SILO$agfunctions <- summaries
  cat(
    "***         SILO stats -->",
    paste0('"', paste(summaries, collapse = '", "'), '"'), "\n"
  )
  return(invisible(x))
}





#' Configure DEA resource download settings
#'
#' @param x
#' @param layers
#' @param summaries
#'
#' @return
#' @export
#'
#' @examples
config_dea <- function(x, layers = NULL, summaries = NULL) {

  # reject if not class 'harvester'
  is_cl_harvester(x)
  # Process layers, and warn if a layer is not recognised
  layers <- is_valid_source("dea", layers)
  # TODO: warn if summaries not recognised
  # if only one summary is provided, assume it's for all layers
  if (length(summaries) == 1) {
    summaries <- rep(summaries, length(layers))
  }

  # Apply settings
  x$target_sources$DEA$names <- layers
  cat(
    "***         DEA layers -->",
    paste0('"', paste(layers, collapse = '", "'), '"'), "\n"
  )
  x$target_sources$DEA$agfunctions <- summaries
  cat(
    "***          DEA stats -->",
    paste0('"', paste(summaries, collapse = '", "'), '"'), "\n"
  )
  return(invisible(x))
}





#' Configure DEM resource download settings
#'
#' @param x
#' @param layers
#' @param summaries
#'
#' @return
#' @export
#'
#' @examples
config_dem <- function(x, layers = NULL, summaries = NULL) {

  # reject if not class 'harvester'
  is_cl_harvester(x)
  # Process layers, and warn if a layer is not recognised
  layers <- is_valid_source("dem", layers)
  # Force summaries to NA since DEM_1s is already summarised
  if (!is.null(summaries)) {
    cat("Note: DEM data cannot be summarise further.")
  }
  # Apply settings
  x$target_sources$DEM$names <- layers
  cat(
    "***         DEM layers -->",
    paste0('"', paste(layers, collapse = '", "'), '"'), "\n"
  )
  return(invisible(x))
}




# asserts ----


#' Validate if object is of class harvester
#' @noRd
is_cl_harvester <- function(x) {
  if (!("harvester" %in% class(x))) {
    stop("`config_*` functions are for data harvester objects only!")
  }
}



#' Validate if value is a date
#' @noRd
is_dateformat <- function(x, format = "y") {
  !is.na(lubridate::parse_date_time(x, orders = "y"))
  check <- lubridate::parse_date_time(x, orders = "y")
  if (!is.na(check)) {
    return(x)
  } else {
    return(NULL)
  }
}


#' Validate if download layers are available from various sources
#' @noRd
is_valid_source <- function(source, layers) {
  slga <- c(
    "Bulk_Density", "Organic_Carbon", "Clay", "Silt", "Sand", "pH_CaCl2",
    "Available_Water_Capacity", "Total_Nitrogen", "Total_Phosphorus",
    "Effective_Cation_Exchange_Capacity", "Depth_of_Regolith", "Depth_of_Soil"
  )

  silo <- c(
    "daily_rain", "monthly_rain", "max_temp", "min_temp", "vp", "vp_deficit",
    "evap_pan", "evap_syn", "evap_comb", "evap_morton_lake", "radiation",
    "rh_tmax", "rh_tmin", "et_short_crop", "et_tall_crop", "et_morton_actual",
    "et_morton_potential", "et_morton_potential", "mslp"
  )

  dea <- c(
    "ga_ls_ard_3",
    "s2_nrt_granule_nbar_t",
    "s2_ard_granule_nbar_t",
    "ga_ls8c_nbart_gm_cyear_3",
    "ga_ls7e_nbart_gm_cyear_3",
    "ga_ls5t_nbart_gm_cyear_3",
    "ga_ls8c_ard_3",
    "ga_ls7e_ard_3",
    "ga_ls5t_nbart_gm_cyear_3",
    "ga_ls8c_ard_3",
    "ga_ls7e_ard_3",
    "ga_ls5t_ard_3",
    "ga_ls8c_ard_provisional_3",
    "ga_ls7e_ard_provisional_3",
    "ga_ls_ard_provisional_3",
    "s2b_nrt_granule_nbar_t",
    "s2a_nrt_granule_nbar_t",
    "s2_nrt_provisional_granule_nbar_t",
    "s2b_nrt_provisional_granule_nbar_t",
    "s2a_nrt_provisional_granule_nbar_t",
    "s2a_ard_granule_nbar_t",
    "s2b_ard_granule_nbar_t",
    "ga_ls_landcover",
    "ga_ls_landcover_descriptors",
    "ga_ls_fc_3",
    "fcp_rgb",
    "fcp_seasonal_rgb",
    "fcp_green_veg",
    "fcp_non_green_veg",
    "fcp_bare_ground",
    "fcp_seasonal_green_veg",
    "fcp_seasonal_non_green_veg",
    "fcp_seasonal_bare_ground",
    "ls5_fc_albers",
    "ls7_fc_albers",
    "ls8_fc_albers",
    "fc_albers_combined",
    "mangrove_cover_v2_0_2",
    "s2_barest_earth",
    "ls8_barest_earth_mosaic",
    "landsat_barest_earth",
    "ga_ls_tcw_percentiles_2",
    "ga_ls_wo_3",
    "ga_ls_wo_fq_myear_3",
    "ga_ls_wo_fq_cyear_3",
    "ga_ls_wo_fq_apr_oct_3",
    "ga_ls_wo_fq_nov_mar_3",
    "wofs_albers",
    "wofs_annual_summary_statistics",
    "wofs_annual_summary_clear",
    "wofs_annual_summary_wet",
    "wofs_filtered_summary",
    "wofs_summary_clear",
    "wofs_summary_wet",
    "Water Observations from Space Statistics",
    "wofs_filtered_summary_confidence",
    "wofs_apr_oct_summary_statistics",
    "wofs_apr_oct_summary_clear",
    "wofs_apr_oct_summary_wet",
    "wofs_nov_mar_summary_statistics",
    "wofs_nov_mar_summary_clear",
    "wofs_nov_mar_summary_wet",
    "ITEM_V2.0.0",
    "ITEM_V2.0.0_Conf",
    "NIDEM",
    "high_tide_composite",
    "low_tide_composite",
    "ga_s2_ba_provisional_3",
    "alos_displacement",
    "alos_velocity",
    "envisat_displacement",
    "envisat_velocity",
    "radarsat2_displacement",
    "radarsat2_velocity",
    "aster_false_colour",
    "aster_regolith_ratios",
    "aster_aloh_group_composition",
    "aster_aloh_group_content",
    "aster_feoh_group_content",
    "aster_ferric_oxide_composition",
    "aster_ferric_oxide_content",
    "aster_ferrous_iron_content_in_mgoh",
    "aster_ferrous_iron_index",
    "aster_green_vegetation",
    "aster_gypsum_index",
    "aster_kaolin_group_index",
    "aster_mgoh_group_composition",
    "aster_mgoh_group_content",
    "aster_opaque_index",
    "aster_silica_index",
    "aster_quartz_index",
    "multi_scale_topographic_position",
    "weathering_intensity",
    # corrected images
    "blend_sentinel2_landsat_nbart_daily",
    "hltc_high",
    "hltc_low",
    "item_relative",
    "item_stddev",
    "landsat5_nbar_16day",
    "landsat5_nbar_daily",
    "landsat5_nbart_16day",
    "landsat5_nbart_daily",
    "landsat7_nbar_16day",
    "landsat7_nbar_daily",
    "landsat7_nbart_16day",
    "landsat7_nbart_daily",
    "landsat8_nbar_16day",
    "landsat8_nbar_daily",
    "landsat8_nbart_16day",
    "landsat8_nbart_daily",
    "sentinel2_nbart_daily"
  )

  dem <- c("DEM_1s")

  # select list of products
  if (grepl(source, "slga", ignore.case = TRUE)) {
    products <- slga
  } else if (grepl(source, "silo", ignore.case = TRUE)) {
    products <- silo
  } else if (grepl(source, "dea", ignore.case = TRUE)) {
    products <- dea
  } else if (grepl(source, "dem", ignore.case = TRUE)) {
    products <- dem
  }
  # perform check
  # for each item in vector of layers, match to the source list
  newlayers <- sapply(1:length(layers), function(i) {

    if (layers[i] %in% products) {
      out <- layers[i]
    } else {
      out <- products[agrep(layers[i], products, .1,
                        ignore.case = TRUE)]
    }
    # if unable to match, print warning
    if (length(out) == 0) {
      warning(paste0(toupper(source), " layer, '", layers[i],
        "' cannot be matched. Downloads may fail."), call. = FALSE)
      out <- layers[i]
    }
    return(out)
  })
  return(newlayers)
}

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
