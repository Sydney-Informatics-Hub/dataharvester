#' Title
#'
#' @param layer
#' @param bounding_box
#' @param out_path
#' @param resolution
#' @param crs
#' @param format_out
#'
#' @return
#' @export
#'
#' @examples
download_radiometric <- function(layer,
                                 bounding_box,
                                 out_path,
                                 resolution = 1,
                                 crs = "EPSG:4326",
                                 format_out = "GeoTIFF") {
  # Import module
  path <- system.file("python", package = "dataharvester")
  rad <- reticulate::import_from_path("getdata_radiometric",
    path = path,
    delay_load = TRUE
  )
  # Run
  out <- rad$get_radiometric_layers(
    out_path,
    layer,
    bounding_box,
    resolution,
    crs,
    format_out
  )
  return(out)
}
