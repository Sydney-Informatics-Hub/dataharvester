#' A headless version of the Data-Harvester (with some limitations)
#'
#' The [harvest()] function requires a YAML configuration file to work and will
#' perform data aggregation, downloading and logging based on what is parsed
#' from the YAML file. For more information on 'headless' functionality, see the
#' documentation online (site not live yet). A YAML template can be generated
#' using the function [create_yaml()]
#'
#' @param path_to_config `string`: path to YAML config file, e.g. "settings/"
#' @param log_name `string`: name of output log file which contains some
#'   information about downloaded files
#' @param preview `logical`: preview rasters by plotting the first band only
#' @param contour `logical`: add contour lines to the plot. Defaults to FALSE
#'
#' @export
harvest <- function(path_to_config,
  log_name = "download_log",
  preview = FALSE,
  contour = FALSE) {
  harvest <- harvester_module("harvest")
  harvest$run(path_to_config, log_name, preview)
  config <- load_settings(path_to_config)
  if (preview & !is.null(config$infile)) {
    samples <- read.csv(config$infile)
    x <- samples[[config$colname_lat]]
    y <- samples[[config$colname_lng]]
    plot_rasters(config$outpath, contour = contour, points = TRUE, x, y)
  } else if (preview & is.null(config$infile)) {
    plot_rasters(config$outpath, contour = contour)
  }
}

#' Create a YAML configuration file for editing
#'
#' @return a YAML file
#' @export
create_yaml <- function() {
  NULL
}

