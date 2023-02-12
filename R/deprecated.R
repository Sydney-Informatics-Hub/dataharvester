#' Authenticate to Google Earth Engine API
#'
#' @description
#' `r lifecycle::badge("deprecated")`
#'
#' This function was deprecated as we have moved from using a local module to
#' the conda package for `geodata-harvester`.
#'
#' @keywords internal
#' @export
authenticate_ee <- function(auth_mode = "gcloud") {
  lifecycle::deprecate_warn("1.0.0", "authenticate_ee()", "initialise_earthengine()")
  all_modes <- c("gcloud", "notebook", "rstudiocloud", "binder")
  if (!(auth_mode %in% all_modes)) {
    stop('Argument `auth_mode` must be one of "gcloud", "notebook", "rstudiocloud", "binder"')
  }
  path <- system.file("python", package = "dataharvester")
  ee <- harvester_module("getdata_ee")
  # "gcloud", "notebook", "rstudiocloud", "binder"
  if (auth_mode %in% c("rstudiocloud", "binder")) {
    auth_mode <- "notebook"
  }
  ee$initialise(auth_mode = auth_mode)
  return(invisible(TRUE))
}

