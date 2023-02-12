#' Initialise and validate Data-Harvester, including dependencies
#'
#' @param envname Use this Conda environment. Defaults to `"r-reticulate"`
#' @param earthengine Initialise Earth Engine if `TRUE.` Defaults to `FALSE`
#' @param auth_mode Authentication mode to access the GEE API. Using `"gcloud"`
#'   normally works. The remaining three options are identical (`"notebook",
#'   "rstudiocloud", "binder"`), just named differently for context
#'
#' @export
initialise_harvester <- function(
    envname = NULL,
    earthengine = FALSE,
    auth_mode = NULL,
    force_reinstall = FALSE) {
  # Remove environment if force_reinstall = TRUE
  if (force_reinstall) {
    reticulate::conda_remove(envname)
  }
  # Define environment to use
  if (is.null(envname)) {
    message("\u2299 Setting environment to `dataharvester`")
    envname <- "dataharvester"
  }
  tryCatch(
    # Try to activate conda environment
    expr = {
      message("\u2299 Activating conda environment...")
      reticulate::use_condaenv(condaenv = envname)
    },
    error = function(e) {
      # If error occurs, create the environment instead
      message("\n\u2757 Conda environment not found. Creating one now...")
      Sys.sleep(2)
      reticulate:::conda_create(
        envname = envname,
        # packages = c("geodata-harvester"),
        python_version = "3.9"
      )
    },
    finally = {
      # Try to activate the env once more
      reticulate::use_condaenv(condaenv = envname)
      reticulate::import("geodata_harvester", delay_load = TRUE)
      reticulate::import("eeharvest", delay_load = TRUE)
      message(paste0("\u2714 Environment activated"))
    }
  )
  # Activate GEE if earthengine = TRUE
  if (earthengine) {
    message("\u2299 Checking Google Earth Engine authentication")
    initialise_earthengine(auth_mode = auth_mode)
  }

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
