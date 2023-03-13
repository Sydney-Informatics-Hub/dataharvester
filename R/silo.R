#' Download from SILO database
#'
#' @param layernames `r params(layernames)`
#' @param bounding_box `r params(bounding_box)`
#' @param out_path `r params(out_path)`
#' @param date_min `r params(date_min)`
#' @param date_max `r params(date_max)`
#' @param format_out Exported file format. Only `"tif"` is currently available.
#'   Defaults to `"tif"`
#' @param delete_temp Delete any temporary files that were created. Defaults to
#'   `FALSE`
#'
#' @return a list of filenames (after files have been downloaded or processed)
#' @export
download_silo <- function(layernames,
                          bounding_box,
                          out_path,
                          date_min,
                          date_max,
                          format_out = "tif",
                          delete_temp = FALSE) {
  # Import module
  silo <- gdh$getdata_silo

  out <- silo$get_SILO_layers(
      layernames,
      date_min,
      date_max,
      out_path,
      bounding_box,
      format_out,
      delete_temp
    )
  class(out) <- append(class(out), "rasterPath")
  return(out)
}
