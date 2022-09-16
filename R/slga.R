#' Download layers from SLGA data server
#'
#' @param layer
#' @param bounding_box
#' @param out_path
#' @param resolution
#' @param depth_min
#' @param depth_max
#' @param get_ci
#' @param verbose
#'
#' @return
#' @export
#'
#' @examples
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
