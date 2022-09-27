#' Download Geoscience Australia DEM grid data
#'
#' Wrapper funtion to get the layers from the Geoscience Australia DEM 1 arc
#' second grid.
#'
#' @param layer `r params(layer)`
#' @param out_path `r params(out_path)`
#' @param bounding_box `r params(bounding_box)`
#' @param resolution `r params(resolution)`
#'
#' @return a list of filenames (after files have been downloaded or processed)
#' @export
download_dem <- function(layer,
                         out_path,
                         bounding_box,
                         resolution = 1) {
  # Import module
  path <- system.file("python", package = "dataharvester")
  dem <- reticulate::import_from_path("getdata_dem",
    path = path,
    delay_load = TRUE
  )
  out <- dem$get_dem_layers(as.list(layer), out_path, bounding_box)
  return(out)
}
