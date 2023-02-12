#' Initialise and validate Data-Harvester, including dependencies
#'
#' @param envname Use this Conda environment. Defaults to `"r-reticulate"`
#' @param earthengine Initialise Earth Engine if `TRUE.` Defaults to `FALSE`
#' @param auth_mode Authentication mode to access the GEE API. Using `"gcloud"`
#'   normally works. The remaining three options are identical (`"notebook",
#'   "rstudiocloud", "binder"`), just named differently for context
#'
#' @export
initialise_harvester <- function(envname = NULL, earthengine = FALSE,
                                 auth_mode = "gcloud") {
  # Check if conda exists
  restart <- validate_conda()
  if (restart) {
    return(message(
      crayon::bold("\u2691 Please restart R now (Session > Restart R)")
    ))
  }
  # Ensure an envname is specified
  if (is.null(envname)) {
    stop(paste0(
      "Argument `envname` must be specified, for example:\n",
      "  initialise_harvester(envname = 'r-reticulate')"
    ))
  }
  # Check if environment can be loaded
  message("\u2299 Verifying Python configuration...", "\r", appendLF = FALSE)
  tryCatch(
    {
      reticulate::use_condaenv(envname)
      message("\u2714 Using Conda environment: ", envname)
    },
    error = function(e) {
      message(
        "\u2691 Environment '", envname,
        "' not found, will create one now"
      )
      reticulate::conda_create(envname, python_version = "3.9")
      install_dependencies(envname)
      reticulate::use_condaenv(envname)
      message("\u2299 Using Conda environment: ", envname)
    }
  )
  validate_dependencies(envname)
  if (earthengine) {
    message("\u2299 Checking Google Earth Engine authentication")
    authenticate_ee(auth_mode)
  }
  return(invisible(TRUE))
}

#' Authenticate to Google Earth Engine API
#'
#' Utilises google-cloud-sdk to initialise and authenticate to the Earth Engine
#' API. An API token containing the user's credentials is saved locally and can
#' be used to authenticate vial Application Default Credentials.
#'
#' @param auth_mode Authentication mode to access the GEE API. Using `"gcloud"`
#'   normally works. The remaining three options are identical (`"notebook",
#'   "rstudiocloud", "binder"`), just named differently for context
#'
#' @export
authenticate_ee <- function(auth_mode = "gcloud") {
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



#' Check if conda is available
#'
#' @param reinstall Force re-install of miniconda. Defaults to FALSE
#'
#' @export
validate_conda <- function(reinstall = FALSE) {
  # Is conda available? If not, install miniconda
  message("\u2299 Checking Python/Conda install...")
  if (reinstall) {
    reticulate::miniconda_uninstall()
    reticulate::install_miniconda(force = TRUE, update = FALSE)
  } else {
    tryCatch(
      {
        # Report current conda binary and version
        conda_binary <- reticulate::conda_binary()
        message("\u2714 Conda binary: ", conda_binary)
        return(invisible(FALSE))
      },
      error = function(e) {
        message(crayon::red("\u2716 Conda binary not found"))
        text_out <- paste0(
          crayon::bold("\n\nDownload and install Miniconda. "),
          "Miniconda is a minimal installer for Python and Conda and",
          "\n is necessary for `dataharvester` to work.",
          "\nFor more information please see: ",
          "https://docs.conda.io/en/latest/miniconda.html"
        )
        message(paste(strwrap(text_out, width = 80), collapse = "\n"))
        if (interactive()) {
          ans <- readline(paste0(
            "Would you like to install Miniconda now? {Y/n}: "
          ))
        } else {
          ans <- "y"
        }
        # Make sure that the answer can be interpreted
        repeat {
          id <- tolower(substring(ans, 1, 1))
          if (id %in% c("y", "")) {
            reticulate::install_miniconda(
              update = FALSE, force = TRUE
            )
            # Explain how to uninstall miniconda manually
            text_out <- paste0(
              "You may remove miniconda at any time by running:",
              "\n`reticulate::miniconda_uninstall()`",
              "\nin the R console.\n"
            )
            message(text_out)
            return(invisible(TRUE))
          } else if (id == "n") {
            message("Installation aborted.")
            return(invisible(FALSE))
          } else {
            ans <- readline("Please answer yes or no: ")
          }
        }
      }
    )
  }
}
