#' Download from Geosciences Australia's Radiometric Map of Australia
#'
#' @details
#' ## Layers
#'
#' - `radmap2019_grid_dose_terr_awags_rad_2019`
#' - `radmap2019_grid_dose_terr_filtered_awags_rad_2019`
#' - `radmap2019_grid_k_conc_awags_rad_2019`
#' - `radmap2019_grid_k_conc_filtered_awags_rad_2019`
#' - `radmap2019_grid_th_conc_awags_rad_2019`
#' - `radmap2019_grid_th_conc_filtered_awags_rad_2019`
#' - `radmap2019_grid_thk_ratio_awags_rad_2019`
#' - `radmap2019_grid_u2th_ratio_awags_rad_2019`
#' - `radmap2019_grid_u_conc_awags_rad_2019`
#' - `radmap2019_grid_u_conc_filtered_awags_rad_2019`
#' - `radmap2019_grid_uk_ratio_awags_rad_2019`
#' - `radmap2019_grid_uth_ratio_awags_rad_2019`
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
                                 outpath,
                                 resolution = 1,
                                 crs = "EPSG:4326",
                                 format_out = "GeoTIFF") {
  # Import module
  rad <- gdh$getdata_radiometric
  # Run
  out <- rad$get_radiometric_layers(
    outpath,
    layer,
    bounding_box,
    resolution = resolution,
    crs = crs ,
    format_out = format_out
  )
  class(out) <- append(class(out), "rasterPath")
  return(out)
}
