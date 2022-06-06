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
