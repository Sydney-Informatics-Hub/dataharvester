#' Load settings from YAML file
#'
#' @param path
#'
#' @return
#' @export
#'
#' @examples
load_settings <- function(path_to_yaml, to_namespace = TRUE) {
  path <- system.file("python", package = "dataharvester")
  set <- reticulate::import_from_path("settingshandler",
    path = path,
    delay_load = TRUE
  )
  out <- set$main(path_to_yaml, to_namespace)
  return(out)
}
