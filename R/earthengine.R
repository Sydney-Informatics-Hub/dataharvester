#' Define Google Earth Engine data to collect
#'
#' @param collection (str) A Google Earth Engine collection. Collections can be
#'   found on https://developers.google.com/earth-engine/datasets
#' @param coords (list of dbl) GPS coordinates in WGS84 [East, North]. Minimum
#'   of one set of coordinates should be provided to create a point coordinate.
#'   If more than one set of coordinates is provided, a polygon will be created
#' @param date (str) Start date of image(s) to be collected in YYYY-MM-DD or
#'   YYYY format. If YYY-MM-DD is provided, will search the specific date only
#'   (which may not contain an image), unless `end_date` is also provided, which
#'   will collect images between the two dates. If YYYY is provided, all images
#'   within the specified year will be included in the collection
#' @param end_date (str, optional) When paired with `date` argument, can define
#'   a date range in YYYY-MM-DD or YYYY format
#' @param buffer (int, optional) If `coords` is a single point, `buffer` can be
#'   used to create a circular buffer with the specific radius in metres. If
#'   `coords` contains more than one set of coordinates, this argument does
#'   nothing
#' @param bound (logical, optional) If TRUE and `buffer` is set, will convert
#'   circular buffer to a bounding box instead. Defaults to FALSE
#' @param config (str, optional) Path to a configuration file in .yaml format.
#'   When this is provided, all arguments are ignored and the function will
#'   refer to the configuration file to determine argument values
#'
#' @return an object containing attributes necessary to preprocess and and
#'   download images for all other `ee_*()` functions
#' @export
#'
#' @examples
#'
#' ee_collect(collection = "LANDSAT/LC09/C02/T1_L2",
#'            coords = c(149.769345,-30.335861, 149.949173,-30.206271),
#'            date = "2021-06-01",
#'            end_date = "2022-06-01")
#'
ee_collect <- function(collection = NULL,
                    coords = NULL,
                    date = NULL,
                    end_date = NULL,
                    buffer = NULL,
                    bound = FALSE,
                    config = NULL) {
  path <- system.file("python", package = "dataharvester")
  ee <- reticulate::import_from_path("getdata_ee",
                                     path = path,
                                     delay_load = TRUE)
  out <- ee$collect(collection, coords, date,
                    end_date, buffer, bound, config)
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
#' @param object (object) a data object produced by `ee_collect()`
#' @param mask_clouds (logical, optional) if TRUE, will perform cloud and shadow
#'   masking on image(s). Defaults to TRUE
#' @param reduce (str, optional) Summary technique used to reduce an image
#'   collection to a single composite. Defaults to "median"
#' @param spectral (logical, optional) If TRUE, will automatically calculate
#'   spectral index based on [Awesome Spectral
#'   Indices](https://github.com/awesome-spectral-indices/awesome-spectral-indices).
#'   If required bands are not available, the calculation will be skipped.
#'   Defaults to NULL
#' @param clip (logical, optional)
#'
#' @return an updated `ee_collect()` object that can be passed on to `ee_map()`,
#'   `ee_aggregate()` or `ee_download()`
#'
#' @export
#'
#' @examples
#'
#' img <- ee_collect(collection = "LANDSAT/LC09/C02/T1_L2",
#'                   coords = c(149.769345,-30.335861, 149.949173,-30.206271),
#'                   date = "2021-06-01",
#'                   end_date = "2022-06-01")
#'
#' ee_preprocess(img, spectral = "NDVI")
#'
ee_preprocess <- function(object, mask_clouds = TRUE, reduce = "median",
                       spectral = NULL, clip = TRUE) {
  out <- object$preprocess(mask_clouds, reduce, spectral, clip)
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
#' @param object (object) a data object produced by `ee_collect()`
#' @param frequency (str, optional) either `"month"` or `"year"` are accepted
#' @param reduce_by (str, optional) summary statistic or technique to perform on
#'   aggregated data. If NULL (default), will calculate the mean per period
#'
#' @return
#' @export
#'
#' @examples
ee_aggregate <- function(object, frequency = "month", reduce_by = NULL) {
  out <- object$aggregate(frequency, reduce_by)
  return(object)
}

#' Visualise an Earth Engine Image or ImageCollection on an interactive map
#'
#' @param object
#' @param bands
#' @param minmax
#' @param palette
#' @param save_to
#'
#' @return
#' @export
#'
#' @examples
ee_map <- function(object, bands, minmax = NULL, palette = NULL) {
  # generate map
  out <- object$map(bands, minmax, palette, save_to = "temp.html")
  # Plot in RStudio viewer
  rstudioapi::viewer("temp.html")

  return(object)
}


#' Title
#'
#' @param object
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
  out <- object$download(bands, scale, outpath, out_format, overwrite)
  return(object)
}

