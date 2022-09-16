#' Download layers from SLGA data server
#'
#' @param layer `string`: layer name(s) to download
#' @param bounding_box `numeric`: coordinates in EPSG:4326 use to generate a
#'   bounding box around are of interest, i.e. `c(min_x, min_y, max_x, max_y)`
#' @param out_path `string`: path to output folder e.g. 'downloads/'
#' @param resolution `numeric`, `optional`: resolution in arcsec. Defaults to 3
#'   arcsec (~ 90 m), which is the native resolution of SLGA data
#' @param depth_min `integer`, `optional`: SLGA layers are aggregated by depth.
#'   Use `depth_min` and `depth_max` to define specific depths to collect
#' @param depth_max `integer`, `optional`: SLGA layers are aggregated by depth.
#'   Use `depth_min` and `depth_max` to define specific depths to collect
#' @param get_ci `logical`, `optional`: download upper and lower 95% confidence
#'   limits with the the layer. Defaults to TRUE
#' @param verbose `logical`, `optional`: print as much information as possible
#'   to the debug log. Defaults to FALSE
#'
#' @return path name(s) of layer(s) downloaded
#' @export
#'
#' @examples
#' NULL
download_slga <- function(layer,
                          bounding_box,
                          out_path,
                          resolution = 3,
                          depth_min = 0,
                          depth_max = 200,
                          get_ci = TRUE,
                          verbose = FALSE) {

  # Import module
  path <- system.file("python", package = "dataharvester")
  slga <- reticulate::import_from_path("getdata_slga",
    path = path,
    delay_load = TRUE
  )
  # Run
  out <- slga$get_slga_layers(
    layer,
    bounding_box,
    out_path,
    resolution,
    depth_min,
    depth_max,
    get_ci,
    verbose
  )
  return(out)
}
