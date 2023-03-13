#' Initialise and validate Data-Harvester, including dependencies 2
#'
#' @param envname Use this Conda environment. Defaults to `"r-harvester"`
#' @param earthengine Initialise Earth Engine if `TRUE.` Defaults to `FALSE`
#' @param auth_mode Authentication mode to access the GEE API. Using `"gcloud"`
#'   normally works. The remaining three options are identical (`"notebook",
#'   "rstudiocloud", "binder"`), just named differently for context
#'
#' @export

library(reticulate)

initialise_harvester <- function(envname = NULL, earthengine = FALSE,
                                 auth_mode = "gcloud") {
  message("\u2714 Initialise harvester...")
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
      "  initialise_harvester(envname = 'r-harvester')"
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
      use_condaenv(envname)
      message("\u2299 Using Conda environment: ", envname)
      message("\u2299 Installing geodata-harvester package...")
      reticulate::conda_install(
        envname = envname,
        packages = "geodata-harvester",
        channel = "conda-forge"
      )
    }
  )

  validate_dependencies(envname)

  #import geodata-harvester and add to global environment
  message("\u2299 Importing geodata-harvester Python package as gdh")
  .GlobalEnv$gdh <- reticulate::import("geodata_harvester")

  if (earthengine) {
    message("\u2299 Checking Google Earth Engine authentication")
    authenticate_ee(auth_mode)
  }
  message("\u2714 Harvester initialized.")
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

  # import Google eartth engine garvetsre package eeharvets
  message("\u2299 Importing eeharvester Python package as ee")
  eeharvest <- reticulate::import("eeharvest")
  .GlobalEnv$ee <- eeharvest$harvester

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
  message("\n\u2299 Checking Python/Conda install...")
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
        message(crayon::red("\u2716 Conda binary not found"))
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


#' Install Python dependencies for dataharvester
#'
#' @noRd
install_dependencies <- function(envname) {
  # Create environment first

  if (.Platform$OS.type == "windows") {
    windows <- TRUE
  } else {
    windows <- FALSE
  }

  # Install dependencies (geodata-harvester comes with all dependencies)
  reticulate::conda_install(
    envname = envname,
    packages = c("geodata-harvester"),
      channel = "conda-forge"
    )

}

#' Validate Python dependencies for dataharvester
#'
#' Better validations are needed, but this will do for now.
#'
#' @noRd
validate_dependencies <- function(envname = "r-harvester") {
  # Note: a Conda environment must be loaded first or this function will fail
  # List required packages
  message("\n\u2299 Validating dependencies...", "\r", appendLF = FALSE)
  checklist <- c(
    "geodata-harvester"
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
    return(invisible(TRUE))
  } else {
    message(paste0(
      crayon::yellow(
        "\u2691 Not all dependencies are available"
      )
    ))
    message(paste0(
      crayon::yellow(
        "\u2299 Re-installing all dependencies just to be sure..."
      )
    ))
    install_dependencies(envname)
    return(invisible(TRUE))
  }
}
