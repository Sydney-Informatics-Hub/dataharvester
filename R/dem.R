#' Download Geoscience Australia DEM grid data
#'
#' Wrapper funtion to get the layers from the Geoscience Australia DEM 1 arc
#' second grid.
#'
#' @param layer `string`: layer name(s) to download
#' @param out_path `string`: path to output folder e.g. 'downloads/'
#' @param bounding_box `numeric`:
#' @param resolution `integer`, `optional`:
#'
#' @return a list of output filenames
#' @export
#'
#' @examples
#' NULL
download_dem <- function(layer,
                         out_path,
                         bounding_box, zresolution = 1) {
  # Import module
  path <- system.file("python", package = "dataharvester")
  dem <- reticulate::import_from_path("getdata_dem",
    path = path,
    delay_load = TRUE)
  out <- dem$get_dem_layers(as.list(layer), out_path, bounding_box)
  return(out)
}
