#' Download Australian climate data from SILO
#'
#' @param layername NULL
#' @param years NULL
#' @param outpath NULL
#' @param bbox NULL
#' @param format_out NULL
#' @param delete_temp NULL
#' @param verbose NULL
#'
#' @return NULL
#' @export
#'
#' @examples
#' NULL
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
