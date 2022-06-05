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
