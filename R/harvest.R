#' Title
#'
#' @param path_to_config
#' @param ...
#'
#' @return
#' @export
#'
#' @examples
harvest <- function(path_to_config, preview = FALSE) {
  path <- system.file("python", package = "dataharvester")
  ee <- reticulate::import_from_path("harvest", path = path, delay_load = TRUE)
  ee$run(path_to_config, preview = preview)
}
