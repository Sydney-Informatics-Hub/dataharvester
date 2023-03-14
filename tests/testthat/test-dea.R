# generate temp directory


test_that("download_dea: downloads work", {
  skip_on_cran()
  skip_if_no_conda()

  llara <- c(149.7, -30.3, 149.8, -30.2)
  tempDir <- tempfile()
  dir.create(tempDir)

  dea1 <- download_dea(
    layer = "landsat_barest_earth",
    bounding_box = llara,
    out_path = tempDir,
    date_min = "2022-10-01",
    date_max = "2022-11-01",
    resolution = 300
  )
  unlink(dea1)
  dea2 <- download_dea(
    layer = c("landsat_barest_earth", "ga_ls_fc_pc_cyear_3"),
    bounding_box = llara,
    out_path = tempDir,
    date_min = "2022-10-01",
    date_max = "2022-11-01",
    resolution = 300
  )
  expect_true("rasterPath" %in% class(dea2))
  expect_equal(length(dea2), 2)
  unlink(tempDir, recursive = TRUE)
})

