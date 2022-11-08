# Store common manual params here
params <- function(value, default = NULL) {
  # Match
  s <- match.call()
  val <- as.character(s)[2]
  # Define
  layer <- "Layer name(s) to download as a vector of strings"
  bounding_box <- "A numeric vector of coordinate values used to generate a bounding box around are of interest in EPSG:4326 format, for example, `c(min_x, min_y, max_x, max_y)`"
  out_path <- "Path to an output/download folder, e.g. `'downloads/'`"
  years <- "Year(s) to download data from (if available), e.g. `2019:2021` or `c(2015, 2020)`"
  crs <- "Coordinate referencing system (CRS) to use. Currently, only accepts 'EPSG:4326'"
  resolution <- "An integer value for resolution, in arc seconds"
  verbose <- "Print as much information as possible to the debug log"
  # Create list
  all_params <- list(
    layer = layer,
    bounding_box = bounding_box,
    out_path = out_path,
    years = years,
    crs = crs,
    resolution = resolution,
    verbose = verbose
  )
  # Join
  out <- all_params[[val]]
  if (!is.null(default)) {
    out <- paste0(out, ". Defaults to `", default, "`")
  }
  return(out)
}
