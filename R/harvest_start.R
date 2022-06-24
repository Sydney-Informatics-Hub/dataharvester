
#' Initialise and validate Data-Harvester and dependencies
#'
#' @param env
#'
#' @return
#' @export
#'
#' @examples
harvest_start <- function(env = NULL) {
  validate_conda()
  validate_env(env = env)
  validate_py_packages()
}



#' Check if conda is available
#'
#' @param reply `logical` if `interactive()`, function will prompt user for
#'   response. Defaults to TRUE when `interactive()` is chosen.
#'
#' @export
validate_conda <- function(reply = interactive()) {
  # Is conda available? If not, install miniconda
  tryCatch(
    {
      message("Attempting to find a conda installation...",
              appendLF = FALSE)
      conda_binary <- reticulate::conda_binary()
      message("done")
      message(paste("Conda found at path: ", conda_binary))
    },
    error = function(e) {
      text_out <- paste0(
        "Conda binary not detected. You must use Anaconda or  Miniconda to use the AgReFed Data-Harvester. ", crayon::bold("\n\nDownload and install Miniconda. "), "Miniconda is a minimal and open-source installer for Python and conda. For more information see: https://docs.conda.io/en/latest/miniconda.html."
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
          reticulate::install_miniconda()
          text_out <- paste0(
            "You may remove miniconda entirely by running:\n",
            "\nreticulate::miniconda_uninstall()\n",
            "\n in your R console.\n",
            crayon::bold("* Please restart R and re-run `start_harvester()`.")
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


#' Load default conda environment
#'
#' @param env `chr` name of conda environment to load. Defaults to `NULL`, which
#'   automatically searches for the environments `geopy` and `dataharvestR`
#'
#' @export
validate_env <- function(env = NULL) {
  # Try to search for default conda environments "geopy" or "dataharvesteR"
  if (is.null(env)) {
    env <- "geopy"
    tryCatch(
      {
        reticulate::use_condaenv(env)
      },
      error = function(e) {
        tryCatch(
          {
            env <- "dataharvestR"
            reticulate::use_condaenv(env)
          },
          error = function(e) {
            # If both environments are not found, create one for `dataharvestR`
            message("Conda environment  not found. Creating one on the spot...")
            reticulate::conda_create("dataharvestR", packages = "python=3.9")
            reticulate::use_condaenv("dataharvestR")
          }
        )
      }
    )
  } else {
    tryCatch(
      {
        reticulate::use_condaenv(env)
      },
      error = function(e) {
        message(
          "Conda env ", env, " does not currently exist, creating one ",
          "on the spot: "
        )
        try(reticulate::conda_remove(env), silent = TRUE)
        reticulate::conda_create(env, packages = "python=3.9")
        reticulate::use_condaenv(env)
      }
    )
  }
  message(crayon::green("\U2713"), " | ", "conda env    : ", env, "\n")
}



#' Check if required Python packages for Data-Harvester exist.
#'
#' Internal function. First, the function checks if all required packages have
#' been installed. Then it does a quick check to see if gdal is at version
#' 3.4.2.
#' @import dplyr
#' @importFrom rlang .data
#' @returns `logical`
#' @export
validate_py_packages <- function(env = "geopy") {
  # List required packages
  py_packages <- c(
    "gdal",
    "geopandas",
    "ipykernel",
    "netcdf4",
    "numba",
    "owslib",
    "rasterio",
    "rioxarray"
  )
  # Required gdal version
  gdal_required <- "3.4.2"
  # Filter package list for checks
  py_avail_modules <-
    reticulate::py_list_packages()[, 1:2] |>
    dplyr::filter(.data$package %in% py_packages)
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
  if(check_py_packages & check_gdal_version) {
    message(paste(crayon::green("\U2713"), " | ", py_packages, "\n"))
  } else {
    message(paste0("Cannot validate required Python packages. ",
                   "Attempting to reinstall all packages to be safe..."))
    reticulate::conda_install(env, c("gdal == 3.4.2", py_packages[-1]))
  }
  return(invisible(TRUE))
}
