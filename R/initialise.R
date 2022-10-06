#' Initialise and validate Data-Harvester, including dependencies
#'
#' @param envname Use this Conda environment. Defaults to `"r-reticulate"`
#' @param earthengine Initialise Earth Engine if `TRUE.` Defaults to `FALSE`
#'
#' @export
initialise_harvester <- function(envname = NULL, earthengine = FALSE) {
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
      "✘ Environment `envname` must be specified. We recommend",
      " \"r=reticulate\" or a unique name e.g. \"dataharvester\""
    ))
  }
  # Check if environment can be loaded
  message("• Verifying Python configuration...", "\r", appendLF = FALSE)
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
      .install_dependencies(envname)
      reticulate::use_condaenv(envname)
      message("• Using Conda environment: ", envname)
    }
  )
  .validate_dependencies(envname)

  if (earthengine) {
    message("• Checking Google Earth Engine authentication")
    if (terra::gdal() == "3.0.4") {
      message(paste0(
        "\u2691 Cloud/server environment detected. If a browser popup ",
        "does not appear, ignore the warning messages and copy and ",
        "paste the link produced to your web browser to proceed with ",
        "authentication"
      ))
      authenticate_ee("notebook")
    } else {
      authenticate_ee()
    }
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
validate_conda <- function(reinstall = FALSE) {
  # Is conda available? If not, install miniconda
  message("• Checking Python/Conda install...")
  if (reinstall) {
    reticulate::miniconda_uninstall()
    reticulate::install_miniconda(force = TRUE, update = FALSE)
  } else {
    tryCatch(
      {
        conda_binary <- reticulate::conda_binary()
        message("\u2714 Conda binary: ", conda_binary)
        return(invisible(FALSE))
      },
      error = function(e) {
        message(crayon::red("✘ Conda binary not found"))
        text_out <- paste0(
          "You must use Anaconda/Miniconda to use `dataharvester`.",
          crayon::bold("\n\nDownload and install Miniconda. "),
          "Miniconda is a minimalinstaller for Python and Conda.",
          " For more information please see: ",
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
}


.install_dependencies <- function(envname) {
  # Create environment first
  # Horrible way to check if we are on RStudio Cloud by checking GDAL version
  use_pygdal <- FALSE
  if (terra::gdal() == "3.0.4") {
    use_pygdal <- TRUE
  }
  # Install dependencies
  if (use_pygdal) {
    reticulate::conda_install(
      envname = envname,
      packages = c("rasterio==1.2.10", "pygdal==3.0.4.11"),
      pip = TRUE
    )
    reticulate::conda_install(
      envname = envname,
      packages = "google-cloud-sdk",
      channel = "conda-forge"
    )
  } else {
    reticulate::conda_install(
      envname = envname,
      packages = c("gdal", "rasterio", "google-cloud-sdk"),
      channel = "conda-forge"
    )
  }
  # remainder conda installs
  reticulate::conda_install(
    envname = envname,
    packages = c(
      "alive-progress",
      "eemont",
      "geemap",
      "geedim",
      "geopandas",
      "netcdf4",
      "numba",
      "owslib",
      "ipykernel",
      "ipywidgets==7.6.5",
      "earthengine-api",
      "rioxarray",
      "wxee",
      "termcolor"
    ),
    pip = TRUE
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
    message("\u2714 All dependencies validated")
  } else {
    message(paste0(
      crayon::yellow(
        "\u2691 Not all dependencies are available"
      )
    ))
    message(paste0(
      crayon::yellow(
        "• Re-installing all dependencies just to be sure..."
      )
    ))
    .install_dependencies(envname)
  }
}
