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
authenticate_ee <- function() {
  eepy <- dd_source_python("getdata_ee", "dataharvester")
  invisible(eepy$initialise())
}



#' Check if conda is available
#'
#' @param reply `logical` if `interactive()`, function will prompt user for
#'   response. Defaults to TRUE when `interactive()` is chosen.
#'
#' @export
validate_conda <- function(reply = interactive()) {
  # Is conda available? If not, install miniconda
  message("• Checkking python/conda install...")
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
      if (reply) {
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


#' Check if required Python packages for Data-Harvester exist.
#'
#' Internal function. First, the function checks if all required packages have
#' been installed. Then it does a quick check to see if gdal is at version
#' 3.4.2. If any package appears to be missing they will be reinstalled.
#'
#' @param env `chr` name of environment
#'
#' @import dplyr
#' @importFrom rlang .data
#' @returns `logical`
#' @export
validate_py_packages <- function(env = NULL) {
  # List required packages
  py_packages <- c(
    "gdal",
    "geopandas",
    "ipykernel",
    "netcdf4",
    "numba",
    "owslib",
    "rasterio",
    "rioxarray",
    "eemont",
    "geemap",
    "pygis",
    "localtileserver",
    "earthengine-api",
    "geemap",
    "alive-progress"
  )
  # Required gdal version
  gdal_required <- "3.4.2"
  # Filter package list for checks
  py_avail_modules <-
    reticulate::py_list_packages()[, 1:2] |>
    dplyr::filter(.data$package %in% py_packages)
  message("\u2139 Checking package versions")
  # Check that all packages have been installed
  check_py_packages <-
    py_avail_modules |>
    dplyr::pull(.data$package) |>
    setequal(py_packages)
  # Check that gdal version is 3.4.2
  check_gdal_version <-
    py_avail_modules |>
    dplyr::filter(.data$package == "gdal") |>
    dplyr::pull(.data$version) |>
    setequal(gdal_required)
  # If both are TRUE, we are good, otherwise re-install everything to be safe
  if (check_py_packages & check_gdal_version) {
    # message(paste(crayon::green("✔"), py_packages, " | "))
    message(paste(crayon::green("✔ all packages validated")))
  } else {
    message(paste0(
      "Cannot validate required Python packages. ",
      "Attempting to reinstall all packages to be safe..."
    ))
    # reticulate::conda_install(env, c("gdal == 3.4.2", py_packages[-1]))
    pyconfig <- reticulate::py_config()
  }
  return(invisible(TRUE))
}
