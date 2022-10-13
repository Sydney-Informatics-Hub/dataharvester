# Note - "borrowed" from:
# https://github.com/rstudio/reticulate/blob/main/R/testthat-helpers.R


skip_if_no_python <- function() {

  if (identical(getOption("reticulate.python.disabled"), TRUE))
    skip("Python bindings not available for testing")

  if (!reticulate::py_available(initialize = TRUE))
    skip("Python bindings not available for testing")

}

skip_if_no_conda <- function(env = "r-reticulate") {

  skip_on_cran()
  skip_if_no_python()

  if (is.null(tryCatch(reticulate::conda_binary(), error = function(e) NULL)))
    skip("conda not available for testing (can't find conda binary)")

  tryCatch({
    # Test if env loads without error
    reticulate::use_condaenv(env)
  },
    error = function(e) {
      skip("conda environment not available for testing (can't load env)")
    })

  tryCatch({
    # Check if rasterio is in conda env
    reticulate::import("rasterio")
  },
    error = function(e) {
      skip("rasterio not available for testing (can't load rasterio)")
    })

}


# skip_if_no_scipy <- function() {
#
#   skip_on_cran()
#   skip_if_no_python()
#
#   if (!py_module_available("scipy"))
#     skip("scipy not available for testing")
#
#   scipy <- import("scipy")
#   if (clean_version(scipy$`__version__`) < "1.0")
#     skip("scipy version is less than v1.0")
#
# }


