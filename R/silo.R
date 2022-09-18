#' Download Australian climate data from SILO
#'
#' @param layername
#' @param years
#' @param outpath
#' @param bbox
#' @param format_out
#' @param delete_temp
#' @param verbose
#'
#' @return
#' @export
#'
#' @examples
download_silo <- function(layername,
                          years,
                          out_path,
                          bounding_box = NULL,
                          format_out = "nc",
                          delete_temp = FALSE,
                          verbose = FALSE) {
  # Import module
  path <- system.file("python", package = "dataharvester")
  silo <- reticulate::import_from_path("getdata_silo",
    path = path,
    delay_load = TRUE
  )
  out <- silo$get_SILO_raster(
    layername,
    years,
    out_path,
    bounding_box,
    format_out,
    delete_temp,
    verbose
  )
  return(out)
}
