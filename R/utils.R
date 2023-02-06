#' (Internal) Source module stored in inst folder
#'
#' @noRd
harvester_module <- function(module_name) {
  filename <- paste0("python/", module_name, ".py")
  path <- dirname(system.file(filename, package = "dataharvester"))
  out <- reticulate::import_from_path(module_name,
    path = path,
    delay_load = TRUE
  )
  return(out)
}

#' (Internal) Match to one value in a function's argument
#'
#' @noRd
match_single <- function(arg) {
  # credit: https://stackoverflow.com/a/72438444
  arg_name <- as.character(substitute(arg))
  caller_fun <- sys.function(1)
  choices_as_call <- formals(caller_fun)[[arg_name]]
  choices <- eval(choices_as_call)
  if (all(arg %in% choices) & length(arg) == 1) {
    return(arg)
  } else {
    stop(paste0(
      "Argument `", arg_name, "` can only contain one (1) of these ",
      "values: ", toString(choices)
    ))
  }
}

#' (Internal) Match to multiple values in a function's argument
#'
#' @noRd
match_multi <- function(arg) {
  # credit: https://stackoverflow.com/a/72438444
  arg_name <- as.character(substitute(arg))
  caller_fun <- sys.function(1)
  choices_as_call <- formals(caller_fun)[[arg_name]]
  choices <- eval(choices_as_call)
  if (all(arg %in% choices)) {
    return(arg)
  } else {
    stop(paste0(
      "Argument `", arg_name, "` can only contain these values: ",
      toString(choices)
    ))
  }
}


#' Preview all images in a folder, recursively
#'
#' @param path path to folder
#' @param contour show contour lines. Defaults to FALSE
#' @noRd
plot_rasters <- function(path,
                         contour = FALSE,
                         points = FALSE,
                         x = NULL, y = NULL) {
  # Extract image list
  images <- list.files(
    path = path,
    pattern = "\\.tif$",
    recursive = TRUE,
    full.names = TRUE
  )
  # If 1 image, just use the path supplied
  if (length(images) == 0) {
    images <- path
  }
  message(length(images), " images found")
  # Generate matrix grid
  mar <- c(1, 1, 1.5, 1)
  par(mfrow = n2mfrow(length(images)))
  # Plot
  for (i in 1:length(images)) {
    r <- terra::rast(images[i])[[1]]
    terra::plot(r,
      legend = FALSE,
      main = basename(images[i])
    )
    if (contour) terra::contour(r, alpha = 0.5, add = TRUE, nlevels = 5)
    if (points) {
      terra::points(y, x, col = "firebrick", pch = 20, cex = 1)
    }
  }
  par(mfrow = c(1, 1))
}


#' Plot GeoTIFF object
#' @keywords internal
#' @export
plot.rasterPath <- function(x, choose = NULL, band = NULL, ...) {
  # Filter files
  if (!is.null(choose)) {
    x <- x[choose]
  }
  # Create raster object
  raster <- terra::rast(x)
  # Select bands before plotting
  if (!is.null(band)) {
    raster <- raster[[band]]
  }
  terra::plot(raster)
  return(invisible(x))
}

#' Plot Earth Engine object
#' @keywords internal
#' @export
plot.getdata_ee.download <- function(x, band = NULL, ...) {
  raster <- terra::rast(paste0(x$outpath, x$filenames))
  if (!is.null(band)) {
    raster <- raster[[band]]
  }
  terra::plot(raster)
  return(invisible(x))
}



#' Extract values from GeoTIFF image(s)
#'
#' Extract values from one or more GeoTIFF images based on a set of point
#' locations, supplied as (x, y) or (longitude, latitude) coordinates. If a path
#' to a folder is provided, all images in the folder will be processed.
#'
#' @param path path to a folder containing one or more GeoTIFF files e.g.
#'   "~/Documents/rasters", or path pointing to one or more GeoTIFF files e.g.
#'   c("~/rasters/clay.tif", "~/rasters/density.tif")
#' @param xy_coords a data frame of (x, y) or (longitude, latitude) coordinates.
#'   Note the order - incorrect order of coordinates may result in erroneous or
#'   NaN results.
#' @param method one of "simple", which returns the exact value at the cell or
#'   pixel that the point falls in, or "bilinear", which returns a value
#'   interpolated from the values of the four nearest raster cells.
#'
#' @return a data frame of values
#' @export
extract_values <- function(path, xy_coords, method = "simple") {
  .extract_raster <- function(path, xy_coords) {
    out <- terra::extract(terra::rast(path), xy_coords, ID = FALSE)
    return(out)
  }
  # Extract image list from path
  if (all(dir.exists(path))) {
    image_list <- list.files(
      path = path,
      pattern = "\\.tif$",
      recursive = TRUE,
      full.names = TRUE
    )
    data_points <-
      image_list |>
      purrr::map_dfc(~ .extract_raster(.x, xy_coords))
  } else if (all(file.exists(path))) {
    data_points <- .extract_raster(path, xy_coords)
  }
  out <- dplyr::tibble(xy_coords, data_points)
  return(out)
}
