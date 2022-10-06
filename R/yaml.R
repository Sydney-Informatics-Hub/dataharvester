#' Load settings from YAML file
#'
#' @param path Path to settings file in YAML format/extension.
#'
#' @return A settings namespace object
#' @export
load_settings <- function(path_to_yaml) {
  set <- harvester_module("settingshandler")
  out <- set$main(path_to_yaml)
  return(out)
}
