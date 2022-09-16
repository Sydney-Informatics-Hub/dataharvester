#' Define Google Earth Engine data to collect
#'
#' @param collection `string`: name of a Google Earth Engine collection.
#'   Collections can be found on the [Google Earth Engine
#'   Catalog](https://developers.google.com/earth-engine/datasets)
#' @param coords `numeric`: GPS coordinates in WGS84 \[East, North\]. Minimum of
#'   one set of coordinates should be provided to create a point coordinate. If
#'   more than one set of coordinates is provided, a polygon will be created
#' @param date `string`: Start date of image(s) to be collected in YYYY-MM-DD or
#'   YYYY format. If YYY-MM-DD is provided, will search the specific date only
#'   (which may not contain an image), unless `end_date` is also provided, which
#'   will collect images between the two dates. If YYYY is provided, all images
#'   within the specified year will be included in the collection
#' @param end_date `string`, `optional`:  When paired with `date` argument, can
#'   define a date range in YYYY-MM-DD or YYYY format
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
#'   download images for all other `ee_*()` functions
#' @export
#'
#' @examples
#'
#' ee_collect(
#'   collection = "LANDSAT/LC09/C02/T1_L2",
#'   coords = c(149.769345, -30.335861, 149.949173, -30.206271),
#'   date = "2021-06-01",
#'   end_date = "2022-06-01"
#' )
#'
ee_collect <- function(collection = NULL, coords = NULL, date = NULL,
                       end_date = NULL, buffer = NULL, bound = FALSE,
                       config = NULL) {
  path <- system.file("python", package = "dataharvester")
  ee <- reticulate::import_from_path("getdata_ee",
    path = path,
    delay_load = TRUE
  )
  out <- ee$collect(
    collection, coords, date,
    end_date, buffer, bound, config
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
#' by the function, `ee_collect()`
#'
#' @param object `object`: a data object produced by [ee_collect()]
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
#' @return an updated [ee_collect()] object that can be passed on to [ee_map()],
#'   [ee_aggregate()] or [ee_download()]
#'
#' @export
#'
#' @examples
#'
#' img <- ee_collect(
#'   collection = "LANDSAT/LC09/C02/T1_L2",
#'   coords = c(149.769345, -30.335861, 149.949173, -30.206271),
#'   date = "2021-06-01",
#'   end_date = "2022-06-01"
#' )
#'
#' ee_preprocess(img, spectral = "NDVI")
#'
ee_preprocess <- function(object, mask_clouds = TRUE, reduce = "median",
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
#' @param object `object`: a data object produced by [ee_collect()]
#' @param frequency `str`, `optional`: either `"month"` or `"year"` are accepted
#' @param reduce_by `str`, `optional`: summary statistic or technique to perform on
#'   aggregated data. If NULL (default), will calculate the mean per period
#'
#' @return an updated [ee_collect()] object that can be passed on to [ee_map()],
#'   or [ee_download()]
#' @export
#'
#' @examples
#'
#' img <- ee_collect(
#'   collection = "LANDSAT/LC09/C02/T1_L2",
#'   coords = c(149.769345, -30.335861, 149.949173, -30.206271),
#'   date = "2021-06-01",
#'   end_date = "2022-06-01"
#' )
#'
#' ee_preprocess(img, spectral = "NDVI")
#' # ee_aggregate(img, reduce_by = "median")
#'
ee_aggregate <- function(object, frequency = "month", reduce_by = NULL) {
  object$aggregate(frequency, reduce_by)
  return(object)
}

#' Visualise an Earth Engine Image or Image Collection on an interactive map
#'
#' A [folium](http://python-visualization.github.io/folium/) map is produced and
#' image(s) collected so far are displayed as layer(s) on top of the map.
#'
#' @param object `object`: a data object produced by [ee_collect()]
#' @param bands
#' @param minmax
#' @param palette
#'
#' @return
#' @export
#'
#' @examples
ee_map <- function(object, bands, minmax = NULL, palette = NULL) {
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
#' @param object (object) a data object produced by `ee_collect()`
#' @param bands
#' @param scale
#' @param outpath
#' @param out_format
#' @param overwrite
#'
#' @return
#' @export
#'
#' @examples
ee_download <- function(object, bands = NULL, scale = NULL, outpath = NULL,
                        out_format = NULL, overwrite = TRUE) {
  object$download(bands, scale, outpath, out_format, overwrite)
  return(object)
}
