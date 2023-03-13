#' Download from SLGA Landscape Attributes
#'
#' @details
#' ## Layers
#'
#' - `Prescott_index`
#' - `net_radiation_jan`
#' - `net_radiation_july`
#' - `total_shortwave_sloping_surf_jan`
#' - `total_shortwave_sloping_surf_july`
#' - `Slope`
#' - `Slope_median_300m`
#' - `Slope_relief_class`
#' - `Aspect`
#' - `Relief_1000m`
#' - `Relief_300m`
#' - `Topographic_wetness_index`
#' - `TPI_mask`
#' - `SRTM_TopographicPositionIndex`
#' - `Contributing_area`
#' - `MrVBF`
#' - `Plan_curvature`
#' - `Profile_curvature`
#'
#' @param layernames `r params(layernames)`
#' @param bounding_box `r params(bounding_box)`
#' @param out_path `r params(out_path)`
#' @param resolution ` r params(resolution)`
#'
#' @return a list of filenames (after files have been downloaded or processed)
#' @export
#'
download_landscape <- function(layernames,
                               bounding_box,
                               out_path,
                               resolution = 3) {
  # Import module
  landscape <- gdh$getdata_landscape
  # Run
  out <- landscape$get_landscape_layers(
    layernames,
    bounding_box,
    out_path,
    resolution
  )
  class(out) <- append(class(out), "rasterPath")
  return(out)
}
