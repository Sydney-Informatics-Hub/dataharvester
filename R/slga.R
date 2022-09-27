#' Download from SLGA (Soil Atributes)
#'
#' Wrapper funtion to get layers from the Soil and Landscape Grid of Australia
#' (SLGA).
#'
#' @param layer `r params(layer)`
#' @param bounding_box `r params(bounding_box)`
#' @param out_path `r params(out_path)`
#' @param resolution `r params(resolution)`
#' @param depth_min,depth_max SLGA layers can be filtered between specific
#'   depths. Minimum and maximum depths can be set using `depth_min` and
#'   `depth_max`. Defaults to `0` and `200`, respectively
#' @param get_ci Also download upper and lower 95% confidence limits with the
#'   the layer. Defaults to `TRUE`
#' @param verbose `r params(verbose)`
#'
#' @return a list of filenames (after files have been downloaded or processed)
#' @export
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
