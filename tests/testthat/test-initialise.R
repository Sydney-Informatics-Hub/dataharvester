library(reticulate)

test_that("error if no envname is provided during initialisation", {
  skip_on_cran()
  skip_if_no_conda()

  expect_error(initialise_harvester())
})

test_that("full initialisation of env for dataharvester works", {
  skip_on_cran()
  skip_if_no_conda()

  expect_true(initialise_harvester(envname = "r-reticulate"))
})

test_that("earthengine validation works if token is available", {
  skip_on_cran()
  skip_if_no_conda()

  expect_true(authenticate_ee())
})

test_that("error if auth_mode is not in earthengine authenticate list", {
  skip_on_cran()
  skip_if_no_conda()

  expect_error(authenticate_ee(auth_mode = "monkey"))
})

# Already run with initialise_harvster():
# test_that("validating dependencies work if env is loaded", {
#   skip_on_cran()
#   skip_if_no_conda()
#   expect_true(.validate_dependencies(envname = "r-reticulate"))
# })




