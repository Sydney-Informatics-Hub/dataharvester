#' Download from Digital Earth Australia
#'
#' Wrapper funtion to get the layers from Digital Earth Australia collections.
#'
#' @param layer `r params(layer)`
#' @param bounding_box `r params(bounding_box)`
#' @param out_path `r params(out_path)`
#' @param years `r params(years)`
#' @param resolution `r params(resolution)`
#' @param crs `r params(crs)`
#' @param format_out Output format, either "GeoTIFF" or "NetCDF". Defaults to
#'   "GeoTIFF"
#'
#' @return a list of filenames (after files have been downloaded or processed)
#' @export
download_dea <- function(layer,
                         bounding_box,
                         out_path,
                         years,
                         resolution,
                         crs = "EPSG:4326",
                         format_out = "GeoTIFF") {
  # Import module
  dea <- harvester_module("getdata_dea")
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
  class(out) <- append(class(out), "rasterPath")
  return(out)
}
