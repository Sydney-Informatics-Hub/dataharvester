# dd_source_python <- function(modulename, rpackage, report = FALSE) {
#   filename <- paste0("python/", modulename, ".py")
#   path <- dirname(system.file(filename, package = rpackage))
#   if (report) {
#     message(paste0("Loading ", modulename, " module from ", path))
#   }
#   reticulate::import_from_path(modulename, path, convert = FALSE)
# }

#' (Internal) Source module stored in inst folder
#'
#' @export
#' @noRd
harvester_module <- function(module_name) {
  # path <- system.file("python", package = "dataharvester")
  filename <- paste0("python/", module_name, ".py")
  path <- dirname(system.file(filename, package = "dataharvester"))
  out <- reticulate::import_from_path(module_name, path = path,
    delay_load = TRUE)
  return(out)
}

#' (Internal) Match to one value in a function's argument
#'
#' @export
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
#' @export
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

#' Create a dataframe to store raster download and processing information
#'
#' This functions does not have any arguments. The dataframe can be updated with
#' the [update_logtable()] function.
#'
#' @return a data frame object
#' @export
init_logtable <- function() {
  # Import module
  utils <- harvester_module("utils")
  # Run
  out <- utils$init_logtable()
  return(out)
}

#' Update download and processing dataframe
#'
#' Update the dataframe table with the information from the raster download or
#' processing. The dataframe is simultaneoulsy saved to a csv file in default
#' output directory.
#'
#' @param logname `string`: name of data frame object created from
#'   `init_logfile()`
#' @param file_name `string`: file name(s) to add to the data frame
#' @param layer `string`: layer name(s) to add to the data frame
#' @param source `string`: the download source, abbreviated. For example, "DEA"
#' @param settings `object`: a settings object
#' @param layertitles `string` : layer title(s) to add to the data frame, used
#'   in certain situations e.g. labels for summary plots
#' @param agfunctions aggregation/summary functions used (e.g. mean) or an
#'   specified aggregation requested (e.g. 0-5 m) for the layer
#' @param loginfos `string`: status of layer, e.g. "processed"
#'
#' @return a data frame object
#' @export
#'
#' @examples
#' NULL
update_logtable <- function(logname,
                            file_name,
                            layer,
                            source,
                            settings,
                            layertitles = list(),
                            agfunctions = list(),
                            loginfos = list()) {
  # Import module
  utils <- harvester_module("utils")
  # Run
  out <- utils$update_logtable(
    df_log,
    filenames,
    layernames,
    datasource,
    settings,
    layertitles,
    agfunctions,
    loginfos
  )
  return(out)
}


#' Preview all images in a folder, recursively
#'
#' @param path path to folder
#' @param contour show contour lines. Defaults to FALSE
#' @noRd
#'
#' @export
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
      terra::points(y, x, col = 'firebrick', pch = 20, cex = 1)

    }
  }
  par(mfrow = c(1, 1))
}


raster_query <- function(longs, lats, download_log = NULL, rasters = NULL, names = NULL) {
  # Import module
  utils <- harvester_module("utils")
  out <- utils$raster_query(longs, lats, rasters, titles = names)
  return(out)
}


#' Plot GeoTIFF object
#' @export
plot.rasterPath <- function(x, choose = NULL, index = NULL, ...) {
  # Filter files
  if (!is.null(choose)) {
    x <- x[choose]
  }
  # Create raster object
  raster <- terra::rast(x)
  # Select bands before plotting
  if (!is.null(index)) {
    raster <- raster[[index]]
  }
  terra::plot(raster)

#' Plot Earth Engine object
#' @export
plot.getdata_ee.download <- function(x, band = NULL, ...) {
  raster <- terra::rast(paste0(x$outpath, x$filenames))
  if (!is.null(band)) {
    raster <- raster[[band]]
  }
  terra::plot(raster)
  return(invisible(x))
}
}
