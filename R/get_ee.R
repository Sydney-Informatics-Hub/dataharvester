#' Start harvest instance
#'
#' @param config
#' @param collection
#' @param coords
#' @param date
#' @param end_date
#' @param buffer
#' @param bound
#'
#' @return
#' @export
#'
#' @examples
harvest_ee <- function(config = NULL,
                       collection = NULL,
                       coords = NULL,
                       date = NULL,
                       end_date = NULL,
                       buffer = NULL,
                       bound = FALSE) {
  ee <- dd_source_python("getdata_ee", "dataharvestR")
  harvest <- ee$harvest_ee(config, collection, coords, date, end_date, buffer, bound)
  return(harvest)
}

#' Preproces image collection
#'
#' @param ee
#' @param mask_clouds
#' @param reduce
#' @param clip
#' @param spectral
#'
#' @return
#' @export
#'
#' @examples
preprocess_ee <- function(ee, mask_clouds=TRUE, reduce = "median", spectral = NULL, clip = TRUE) {
  prep = ee$preprocess(mask_clouds, reduce, spectral, clip)

  return(prep)
}


#' Preview ee image
#'
#' @param ee
#' @param bands
#' @param minmax
#' @param palette
#'
#' @import htmltools rstudioapi
#'
#' @return
#' @export
#'
#' @examples
#'
map_ee <- function(ee, bands, minmax=NULL, palette=NULL) {
  html_file <- "geemap.html"
  ee$map(bands, minmax, palette, save_to = html_file)
  rstudioapi::viewer(html_file)
  # unlink(html_file)
}
#
# map_ee <- function(ee, bands, minmax=NULL, palette=NULL) {
#   # create temp file path for map output
#   temp_path <- tempfile()
#   filename <- "temp.html"
#   html_file <- file.path(temp_path, filename)
#   # save map to temp directory so we can push it to RStudio's Viewer pane
#   Map <- ee$preview(ee_image, bands, minmax, scale, palette, save_to = html_file)
#   rstudio_viewer(filename, temp_path)
#   unlink(html_file)
# }
