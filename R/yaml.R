#' Load settings from YAML file
#'
#' @param path_to_yaml Path to settings file in YAML format/extension.
#'
#' @return A settings namespace object
#' @export
load_settings <- function(path_to_yaml) {
  # import geodata-harvester settingshandler
  set <- gdh$settingshandler
  out <- set$main(path_to_yaml, to_namespace = FALSE)
  return(out)
}
