#' A headless version of the Data-Harvester (with some limitations)
#'
#' The [harvest()] function requires a YAML configuration file to work and will
#' perform data aggregation, downloading and logging based on what is parsed
#' from the YAML file. For more information on 'headless' functionality, see the
#' documentation online (site not live yet).
#'
#' @param path_to_config `string`: path to YAML config file, e.g. "settings/"
#' @param log_name `string`: name of output log file which contains some
#'   information about downloaded files
#' @param plot `logical`: present a matrix plot of the first band of every image
#'   downloaded. Defaults to FALSE
#' @param contour `logical`: add contour lines to the plot. Defaults to FALSE
#'
#' @importFrom grDevices n2mfrow
#' @importFrom graphics par
#' @importFrom utils read.csv
#'
#' @export
harvest <- function(path_to_config,
                    log_name = "download_log",
                    plot = FALSE,
                    contour = FALSE) {
  # ensure that the full path is known when transferring to Python
  path_to_config <- normalizePath(path_to_config)
  harvest <- harvester_module("harvest")
  harvest$run(path_to_config, log_name, preview = FALSE)
  config <- load_settings(path_to_config)
  if (plot & !is.null(config$infile)) {
    samples <- read.csv(config$infile)
    x <- samples[[config$colname_lat]]
    y <- samples[[config$colname_lng]]
    plot_rasters(config$outpath, contour = contour, points = TRUE, x, y)
  } else if (plot & is.null(config$infile)) {
    plot_rasters(config$outpath, contour = contour)
  }
}
