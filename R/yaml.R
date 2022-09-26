#' Load settings from YAML file
#'
#' @param path Path to settings file in YAML format/extension.
#'
#' @return A settings namespace object
#' @export
load_settings <- function(path_to_yaml, to_namespace = TRUE) {
  path <- system.file("python", package = "dataharvester")
  set <- reticulate::import_from_path("settingshandler",
    path = path,
    delay_load = TRUE
  )
  out <- set$main(path_to_yaml, to_namespace)
  return(out)
}
