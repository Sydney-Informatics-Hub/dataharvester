#' Download Geoscience Australia DEM grid data
#'
#' Wrapper funtion to get the layers from the Geoscience Australia DEM 1 arc
#' second grid.
#'
#' @details
#' Only the layer `DEM_1s` is used right now and can be called with just `DEM`.
#'
#' @param layer `r params(layer)`
#' @param out_path `r params(out_path)`
#' @param bounding_box `r params(bounding_box)`
#' @param resolution `r params(resolution)`
#'
#' @return a list of filenames (after files have been downloaded or processed)
#' @export
download_dem <- function(layer,
                         bounding_box,
                         out_path,
                         resolution = 1) {
  # Import module
  gd <- reticulate::import("geodata_harvester")
  out <-
    gd$getdata_dem$get_dem_layers(
      layernames = list(layer),
      outpath = out_path,
      bbox = bounding_box,
      resolution = resolution
    )
  class(out) <- append(class(out), "rasterPath")
  return(out)
}
