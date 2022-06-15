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
  message("Loading default conda environment...")
  tryCatch(
    {
      reticulate::use_condaenv("geopy")
      message("Conda environment 'geopy' loaded")
    },
    error = function(e) {
      tryCatch(
        {
          reticulate::use_condaenv("dataharvestR")
          message("Conda environment 'dataharvestR' loaded")
        },
        error = function(e) {
          # If both environments are not found, create one for `dataharvestR`
          message("Conda environment  not found. Creating one on the spot...")
          reticulate::conda_create("dataharvestR", packages = "python=3.9")
          reticulate::use_condaenv("dataharvestR")
          message(paste0("Conda environment 'dataharvestR' loaded"))
        }
      )
    }
  )
  # Use py_config() as a means to validate packages
  ver <- reticulate::py_config()
  message("Python packages validated")
}

