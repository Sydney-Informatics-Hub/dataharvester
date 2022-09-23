#' Title
#'
#' @param layer
#' @param bounding_box
#' @param out_path
#' @param years
#' @param resolution
#' @param crs
#' @param format_out
#'
#' @return
#' @export
#'
#' @examples
download_dea <- function(layer,
                         bounding_box,
                         out_path,
                         years,
                         resolution,
                         crs = "EPSG:4326",
                         format_out = "GeoTIFF") {
  # Import module
  path <- system.file("python", package = "dataharvester")
  dea <- reticulate::import_from_path("getdata_dea",
    path = path,
    delay_load = TRUE
  )
  # Run
  out <- dea$get_dea_layers(
    layer,
    years,
    bounding_box,
    resolution,
    out_path,
    crs,
    format_out
  )
  return(out)
}
