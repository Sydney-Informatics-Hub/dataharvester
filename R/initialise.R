#' Initialise and validate Data-Harvester, including dependencies
#'
#' @param earthengine `logical` initialise Earth Engine if TRUE. Defaults to FALSE
#' @import reticulate
#' @export
initialise_harvester <- function(env = "r-reticulate", earthengine=TRUE) {
  # Check that conda is installed
  restart <- validate_conda()
  if (restart) {
    return(message(crayon::bold("⚑ Please restart R now (Session > Restart R)")))
  }
  # If we set this up right, this should trigger auto install of dependencies
  tryCatch(
    {
      # Try to use conda environment
      reticulate::use_condaenv(env)
    },
    error = function(e) {
      # If error, create conda environment
      reticulate::conda_create(env, python_version = "3.9")
      reticulate::use_condaenv(env)
    }
  )
  message("• Verifying python configuration...")
  # kickstart python env (if not already done)
  env = basename(reticulate::py_config()$pythonhome)
  message(crayon::green("✔ "), "Using conda environment '", env, "'")
  # Check if we need GEE
  if (earthengine) {
    message("• Starting Earth Engine authetication...")
    authenticate_ee()
  }

}


#' Authenticate to Google Earth Engine API
#'
#' Utilises google-cloud-sdk to initialise and authenticate to the Earth Engine
#' API. An API token containing the user's credentials is saved locally and can
#' be used to authenticate vial Application Default Credentials.
#'
#' @export
authenticate_ee <- function(auth_mode = "gcloud") {
  path <- system.file("python", package = "dataharvester")
  ee <- reticulate::import_from_path("getdata_ee",
    path = path,
    delay_load = TRUE
  )
  ee$initialise(auth_mode = auth_mode)
}



#' Check if conda is available
#'
#' @param reply `logical` if `interactive()`, function will prompt user for
#'   response. Defaults to TRUE when `interactive()` is chosen.
#'
#' @export
validate_conda <- function() {
  # Is conda available? If not, install miniconda
  message("• Checking python/conda install...")
  tryCatch(
    {
      conda_binary <- reticulate::conda_binary()
      message(crayon::green("✔ "), "Conda binary: ", conda_binary)
      return(invisible(FALSE))
    },
    error = function(e) {
      message(crayon::red("✘ Conda binary not found"))
      text_out <- paste0(
        "You must use Anaconda or Miniconda to use `dataharvester`.",
        crayon::bold("\n\nDownload and install Miniconda. "),
        "Miniconda is a minimal, open-source installer for Python and conda. ",
        "For more information please see: https://docs.conda.io/en/latest/miniconda.html"
      )
      message(paste(strwrap(text_out, width = 80), collapse = "\n"))
      if (interactive()) {
        ans <- readline("Would you like to install Miniconda now? {Y/n}: ")
      } else {
        ans <- "y"
      }
      # Make sure that the answer can be interpreted
      repeat {
        id <- tolower(substring(ans, 1, 1))
        if (id %in% c("y", "")) {
          reticulate::install_miniconda(force = TRUE)
          text_out <- paste0(
            "You may remove miniconda entirely by running:\n",
            "\nreticulate::miniconda_uninstall()\n",
            "\nin your R console.\n"
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

.validate_dependencies <- function(envname = "r-reticulate") {
  # Note: a Conda environment must be loaded first or this function will fail
  # List required packages
  message("• Validating dependencies...", "\r", appendLF = FALSE)
  checklist <- c(
    # pip
    "alive-progress",
    "eemont",
    "geemap",
    "geedim",
    "geopandas",
    "netcdf4",
    "numba",
    "owslib",
    "ipykernel",
    "ipywidgets",
    "earthengine-api",
    "rioxarray",
    "wxee",
    "termcolor",
    # conda
    # "gdal",
    "rasterio",
    "google-cloud-sdk"
  )
  # Filter package list for checks
  py_avail_modules <-
    reticulate::py_list_packages()[, 1:2] |>
    dplyr::filter(.data$package %in% checklist)

  dependencies_ok <-
    py_avail_modules |>
    dplyr::pull(.data$package) |>
    setequal(checklist)

  if (dependencies_ok) {
    message("✔ All dependencies validated")
  } else {
    message(paste(crayon::yellow("⚑ Looks like some packages are not installed or have changed. ")))
    message(paste(crayon::yellow("Re-installing all dependencies just to be sure...")))
    .install_dependencies(envname)
  }
}
