# load_config() -----
test_that("load_config() uses a default config when no argument is provided", {
  test_config <- default_config
  class(test_config) <- append(class(test_config), "harvester")
  expect_equal(load_config(), test_config)
})
