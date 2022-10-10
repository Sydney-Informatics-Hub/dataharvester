#' Download from SLGA Landscape Attributes
#'
#' @param layer `r params(layer)`
#' @param bounding_box `r params(bounding_box)`
#' @param out_path `r params(out_path)`
#' @param resolution ` r params(resolution)`
#'
#' @return a list of filenames (after files have been downloaded or processed)
#' @export
#'
download_landscape <- function(layer, bounding_box, out_path, resolution = 3) {
  # Import module
  landscape <- harvester_module("getdata_landscape")
  # Run
  out <- landscape$get_landscape_layers(
    layer,
    bounding_box,
    out_path,
    resolution
  )
  class(out) <- append(class(out), "rasterPath")
  return(out)
}

