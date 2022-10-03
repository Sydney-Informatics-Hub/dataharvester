#' A headless version of the Data-Harvester (with some limitations)
#'
#' The [harvest()] function requires a YAML configuration file to work and will
#' perform data aggregation, downloading and logging based on what is parsed
#' from the YAML file. For more information on 'headless' functionality, see the
#' documentation online (site not live yet). A YAML template can be generated
#' using the function [create_yaml()]
#'
#' @param path_to_config `string`: path to YAML config file, e.g. "settings/"
#' @param preview `logical`: preview
#'
#' @export
harvest <- function(path_to_config, preview = FALSE) {
  path <- system.file("python", package = "dataharvester")
  ee <- reticulate::import_from_path("harvest", path = path, delay_load = TRUE)
  ee$run(path_to_config, preview = preview)
}

#' Create a YAML configuration file for editing
#'
#' @return a YAML file
#' @export
create_yaml <- function() {
  NULL
}
