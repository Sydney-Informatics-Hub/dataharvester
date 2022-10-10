#' Download from Geosciences Australia's Radiometric Map of Australia
#'
#' @param layer `r params(layer)`
#' @param bounding_box `r params(bounding_box)`
#' @param out_path `r params(out_path)`
#' @param resolution `r params(resolution)`
#' @param crs `r params(crs)`
#' @param format_out File format of downloaded file. Can only be `"GeoTIFF"` or
#'   `"NetCDF"`. Defaults to `"GeoTIFF"`
#'
#' @return a list of filenames (after files have been downloaded or processed)
#' @export
download_radiometric <- function(layer,
                                 bounding_box,
                                 out_path,
                                 resolution = 1,
                                 crs = "EPSG:4326",
                                 format_out = "GeoTIFF") {
  # Import module
  rad <- harvester_module("getdata_radiometric")
  # Run
  out <- rad$get_radiometric_layers(
    out_path,
    layer,
    bounding_box,
    resolution,
    crs,
    format_out
  )
  class(out) <- append(class(out), "rasterPath")
  return(out)
}
