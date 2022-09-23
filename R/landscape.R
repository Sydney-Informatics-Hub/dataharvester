#' Title
#'
#' @param layer
#' @param bounding_box
#' @param out_path
#' @param resolution
#'
#' @return
#' @export
#'
#' @examples
download_landscape <- function(layer, bounding_box, out_path, resolution = 3) {
  # Import module
  path <- system.file("python", package = "dataharvester")
  landscape <- reticulate::import_from_path("getdata_landscape",
    path = path,
    delay_load = TRUE
  )
  # Run
  out <- landscape$get_landscape_layers(
    layer,
    bounding_box,
    out_path,
    resolution
  )
  return(out)
}

