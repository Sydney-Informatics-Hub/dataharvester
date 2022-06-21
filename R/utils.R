#' Source python module stored in Data-Harvester Python folder
#'
#' @param modulename
#' @param rpackage
#' @param report
#'
#' @export
dd_source_python <- function(modulename, rpackage, report = FALSE) {
  filename <- paste0("python/", modulename, ".py")
  path <- dirname(system.file(filename, package = rpackage))
  if (report) {
    message(paste0("Loading ", modulename, " module from ", path))
  }
  reticulate::import_from_path(modulename, path, convert = FALSE)
}
