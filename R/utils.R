#' Source python module stored in Data-Harvester Python folder
#' @noRd
dd_source_python <- function(modulename, rpackage, report = FALSE) {
  filename <- paste0("python/", modulename, ".py")
  path <- dirname(system.file(filename, package = rpackage))
  if (report) {
    message(paste0("Loading ", modulename, " module from ", path))
  }
  reticulate::import_from_path(modulename, path, convert = FALSE)
}

#' View an HTML file in the RStudio Viewer pane.
#'
#' View an HTML file (e.g., a rendered R Markdown document) in the RStudio
#' Viewer pane without re-rendering the R Markdown document.
#'
#' @param file_name The HTML file to be viewed.
#' @param file_path The path to the directory in which the HTML file can be
#'   found, if the HTML file to be viewed is not in the current working
#'   directory.
#'
#' @export
rstudio_viewer <- function(file_name, file_path = NULL) {
  temporary_file <- tempfile() # create temp path
  dir.create(temporary_file)   # create folder based on temp path
  # ceate path to file, prepending temp folder that was created
  html_file <- file.path(temporary_file, file_name)
  # get full path of working directory if file_path arg is NULL
  current_path <- ifelse(is.null(file_path),
                         getwd(),
                         path.expand(file_path))
  file.copy(file.path(current_path, file_name), html_file)
  rstudioapi::viewer(html_file)
}
# internal copy to temp dir -- meant to use with rstudio viewer but not working
# the viewer shows a blank (but works when HTML file is opened on browser)
# TODO: investigate
copy_to_tempdir <- function(path_perm) {
  dir <- tempfile("geemap")
  dir.create(dir)
  file.copy(path_perm, dir)
  base <- basename(path_perm)
  file.path(dir, base)
}
