#' Define Google Earth Engine data to collect
#'
#' @param path_to_config `string`: path to YAML config file
#'
#' @return an object containing attributes necessary to preprocess and and
#'   download images for all other `*_ee()` functions
#' @export
#'
#' @examples
#'\dontrun{
#' collect_ee(
#'   collection = "LANDSAT/LC09/C02/T1_L2",
#'   coords = c(149.769345, -30.335861, 149.949173, -30.206271),
#'   date = "2021-06-01",
#'   end_date = "2022-06-01"
#' )
#'}
collect_ee <- function(path_to_config) {
  # check if object ee exists, if not install and initialise
  if( !exists("ee") )
  {stop(
  message("Earth Engine not yet initialised,
  Call function initialise_harvester with argument earthengine = TRUE"))
    }
  # run gee with settings file
  out <- ee$auto(config=path_to_config)
  return(out)
}


#' Preprocess an Earth Engine Image or Image Collection
#'
#' Obtain image stacks from a Google Earth Engine catalog collection for
#' processing. Full support for Sentinel-2, Sentinel-3, Landsat 5-9 and most
#' MODIS satellites. Preprocessing performs server-side filtering, cloud
#' masking, scaling and offsetting, calculation of spectral indices and
#' compositing into a single image representing, for example, the median, min,
#' max, mean, quantile or standard deviation of the images. For unsupported
#' collections, certain functions like scaling, offsetting, spectral indices and
#' cloud/shadow masking may not be available. Must be used on an object created
#' by the function, [collect_ee()]
#'
#' @param object `object`: a data object produced by [collect_ee()]
#' @param mask_clouds `logical`, `optional`: perform cloud and shadow masking on
#'   image(s). Defaults to TRUE
#' @param reduce `string`, `optional`: summary technique used to reduce an image
#'   collection to a single composite. Defaults to "median"
#' @param spectral `logical`, `optional`: automatically calculate spectral index
#'   based on [Awesome Spectral Indices](https://is.gd/T1ogFV). If required
#'   bands are not available, the calculation will be skipped. Defaults to NULL
#' @param clip `logical`, `optional`: clip the image (removing surrounding
#'   data). This mostly affects visualisation - the final download will always
#'   respect the bounding box set by `coords`, regardless of this value.
#'   Defaults to TRUE
#'
#' @return an updated [collect_ee()] object that can be passed on to [map_ee()],
#'   [aggregate_ee()] or [download_ee()]
#'
#' @export
#'
#' @examples
#'\dontrun{
#' img <- collect_ee(
#'   collection = "LANDSAT/LC09/C02/T1_L2",
#'   coords = c(149.769345, -30.335861, 149.949173, -30.206271),
#'   date = "2021-06-01",
#'   end_date = "2022-06-01"
#' )
#'
#' preprocess_ee(img, spectral = "NDVI")
#'}
preprocess_ee <- function(object, mask_clouds = TRUE, reduce = "median",
                          spectral = NULL, clip = TRUE) {
  object$preprocess(mask_clouds, reduce, spectral, clip)
  return(object)
}

#' Aggregate an Earth Engine Image Collection by period
#'
#' Performs simple temporal aggregation of Earth Engine Image collections by
#' month or year. For example, it can calculate the maximum normalized
#' difference vegetation index (NDVI) of an area of interest for each year. Note
#' that processing times can increase substantially with an increased number of
#' images.
#'
#' @param object `object`: a data object produced by [collect_ee()]
#' @param frequency `str`, `optional`: either `"month"` or `"year"` are accepted
#' @param reduce_by `str`, `optional`: summary statistic or technique to perform on
#'   aggregated data. If NULL (default), will calculate the mean per period
#'
#' @return an updated [collect_ee()] object that can be passed on to [map_ee()]
#'   or [download_ee()]
#' @export
#'
#' @examples
#'\dontrun{
#' img <- collect_ee(
#'   collection = "LANDSAT/LC09/C02/T1_L2",
#'   coords = c(149.769345, -30.335861, 149.949173, -30.206271),
#'   date = "2021-06-01",
#'   end_date = "2022-06-01"
#' )
#'
#' preprocess_ee(img, spectral = "NDVI")
#' aggregate_ee(img, reduce_by = "median")
#'}
aggregate_ee <- function(object, frequency = "month", reduce_by = NULL) {
  object$aggregate(frequency, reduce_by)
  return(object)
}

#' Visualise an Earth Engine Image or Image Collection on an interactive map
#'
#' A [folium](http://python-visualization.github.io/folium/) map is produced and
#' image(s) collected so far are displayed as layer(s) on top of the map.
#'
#' @param object `object`: a data object produced by [collect_ee()]
#' @param bands `string`, `optional`: a string or list of strings representing
#'   the bands to be visualised. If NULL, will present a list of available bands
#'   to visualise
#' @param minmax `numeric`, `optional`: A list of two integers representing the
#'   minimum and maximum values for image pixel colours in single-band images.
#'   If set to NULL, the min and max values are automatically calculated
#'   Defaults to NULL
#' @param palette `string`, `optional`: A string representing the name of a
#'   palette to be used for map colors. Names are accessed from Matplotlib
#'   Colourmaps as described in
#'   https://matplotlib.org/stable/tutorials/colors/colormaps.html. In addition,
#'   "ndvi", "ndwi" and "terrain" palettes are available. If set to None,
#'   "viridis" is used. Defaults to NULL
#'
#' @return an updated [collect_ee()] object that can be passed on to
#'   [aggregate_ee()] or [download_ee()]
#' @export
#'
#' @examples
#' NULL
map_ee <- function(object, bands = NULL, minmax = NULL, palette = NULL) {
  # Generate filename for html
  tempDir <- tempfile()
  dir.create(tempDir)
  htmlfile <- file.path(tempDir, "index.html")
  object$map(bands, minmax, palette, save_to = htmlfile)
  rstudioapi::viewer(htmlfile)
  return(object)
}


#' Download an Earth Engine Image or Image Collection
#'
#' Images are saved as GeoTIFF (.tif) files containing geospatial data, unless
#' otherwise specified in `out_format`.
#'
#' @param object `object`: a data object produced by [collect_ee()]
#' @param bands `string`: a string or list of strings representing the bands to
#'   be downloaded
#' @param scale `numeric`, `optional`: a number represeting the scale of a pixel
#'   in metres. If set to NULL, will use a scale of 100 m. Defaults to NULL
#' @param out_path `string`, `optional`: a string representing the path to the
#'   output directory. If set to NULL, will use the current working directory
#'   and add a "downloads/" folder. Defaults to NULL
#' @param out_format `string`, `optional`: Save image as GeoTIFF (.tif), JPEG
#'   (.jpg) or PNG (.png). Defaults to .tif
#' @param overwrite `logical`, `optional`: overwrite existing file if it already
#'   exists. Defaults to NULL
#'
#' @export
#'
#' @examples
#' NULL
download_ee <- function(object, bands = NULL, scale = NULL, out_path = NULL,
                        out_format = NULL, overwrite = TRUE) {
  object$download(bands, scale, out_path, out_format, overwrite)
  class(object) <- append(class(object), "getdata_ee.download")
  return(object)
}
