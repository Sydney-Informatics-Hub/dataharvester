
#' Initialise and validate Data-Harvester and dependencies
#'
#' @param env `chr` name of environment. If the environment doesn't currently
#'   exist, one will be created in the same name using the default conda binary
#' @param earthengine `logical` initialise Earth Engine if TRUE. Defaults to FALSE
#'
#' @export
initialise <- function(env = NULL, earthengine = FALSE) {
  cli::cli_h1("Welcome to AgReFed Data-Harvester")
  message("\n\u2139 Checking if dataharvesteR has been set up appropriately")
  tryCatch(
    {
      validate_conda()
      validate_env(env = env)
      validate_py_packages(env = env)
    },
    error = function(e) {
      message("Something went wrong here.")
      return(invisible(FALSE))
    }
  )
  # Initialise Earth Engine is set
  if (earthengine) {
    message("\u2139 Set up Earth Engine API access")
    eepy <- dd_source_python("getdata_ee", "dataharvestR")
    eepy$initialise()
  }
  return(invisible(TRUE))
}




#' Check if conda is available
#'
#' @param reply `logical` if `interactive()`, function will prompt user for
#'   response. Defaults to TRUE when `interactive()` is chosen.
#'
#' @export
validate_conda <- function(reply = interactive()) {
  # Is conda available? If not, install miniconda
  message("\u2139 Check Python/conda install")
  tryCatch(
    {
      conda_binary <- reticulate::conda_binary()
      message(crayon::green("✔ "), "conda binary: ", conda_binary)
    },
    error = function(e) {
      message(crayon::red("\U2717"), "conda binary: NULL")
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
  # Try to search for default conda environments "geopy" or "dataharvester"
  if (is.null(env)) {
    env <- "geopy"
    tryCatch(
      {
        reticulate::use_condaenv(env)
      },
      error = function(e) {
        tryCatch(
          {
            env <- "dataharvester"
            reticulate::use_condaenv(env)
          },
          error = function(e) {
            # If both environments are not found, create one for `dataharvester`
            message("Conda environment  not found. Creating one on the spot...")
            reticulate::conda_create("dataharvester", packages = "python=3.9")
            reticulate::use_condaenv("dataharvester")
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
  message(crayon::green("✔ "), "conda env: ", env, "\n")
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
