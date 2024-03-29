#' Define Google Earth Engine data to collect
#'
#' @param collection `string`: name of a Google Earth Engine collection.
#'   Collections can be found on the [Google Earth Engine
#'   Catalog](https://developers.google.com/earth-engine/datasets)
#' @param coords `numeric`: GPS coordinates in WGS84 \[East, North\]. Minimum of
#'   one set of coordinates should be provided to create a point coordinate. If
#'   more than one set of coordinates is provided, a polygon will be created
#' @param date_min `string`: Start date of image(s) to be collected in YYYY-MM-DD or
#'   YYYY format. If YYY-MM-DD is provided, will search the specific date only
#'   (which may not contain an image), unless `end_date` is also provided, which
#'   will collect images between the two dates. If YYYY is provided, all images
#'   within the specified year will be included in the collection
#' @param date_max `string`:  End date of image(s) to be collected in YYYY-MM-DD or
#'   YYYY format.
#' @param buffer `integer`, `optional`: If `coords` is a single point, `buffer`
#'   can be used to create a circular buffer with the specific radius in metres.
#'   If `coords` contains more than one set of coordinates, this argument does
#'   nothing
#' @param bound `logical`, `optional`: If `buffer` contains an integer value,
#'   this agrument will convert the circular buffer to a bounding box instead.
#'   Defaults to FALSE
#' @param config `string`, `optional`: Path to a configuration file in .yaml
#'   format. When this is provided, all arguments are ignored and the function
#'   will refer to the configuration file to determine argument values
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
#'   date_min = "2021-06-01",
#'   date_max = "2021-07-01"
#' )
#'}
collect_ee <- function(collection = NULL, coords = NULL, date_min = NULL,
                       date_max = NULL, buffer = NULL, bound = FALSE,
                       config = NULL) {
  # check if object ee exists, if not install and initialise
  if( !exists("ee") )
  {stop(
    message("Earth Engine not yet initialised,
  Call function initialise_harvester with argument earthengine = TRUE"))
  }
  # run gee with settings file
  out <- ee$collect(
    collection,
    coords,
    date_min,
    date_max,
    buffer = buffer,
    config = config,
    bound = bound
  )
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
#'   date_min = "2021-06-01",
#'   date_max = "2021-07-01"
#' )
#'
#' preprocess_ee(img, spectral = "NDVI")
#'}
preprocess_ee <- function(object, mask_clouds = TRUE, reduce = "median",
                          spectral = NULL, clip = TRUE) {
  object$preprocess(mask_clouds = mask_clouds,
                    reduce = reduce,
                    spectral = spectral,
                    clip = clip)
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
#'   date_min = "2021-06-01",
#'   date_max = "2021-07-01"
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
  object$download(bands,
                  scale =scale ,
                  out_path = out_path,
                  out_format = out_format,
                  overwrite = overwrite)
  class(object) <- append(class(object), "getdata_ee.download")
  return(object)
}

#' @param path_to_config `string`: path to YAML config file
#'
#' @return an object containing attributes necessary to preprocess and and
#'   download images for all other `*_ee()` functions
#' @export
auto_ee <- function(path_to_config) {
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
