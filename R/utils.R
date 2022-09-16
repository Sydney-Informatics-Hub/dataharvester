#' (Internal) Source module stored in python folder
#'
#' @param modulename
#' @param rpackage
#' @param report
#'
#' @export
dd_source_python <- function(modulename, rpackage, report = FALSE) {
  filename <- paste0("python/", modulename, ".py")
  path <- dirname(system.file(filename, package = rpackage))
  if (report) {
    message(paste0("Loading ", modulename, " module from ", path))
  }
  reticulate::import_from_path(modulename, path, convert = FALSE)
}

#' Match to one value in a function's argument
#'
#' @param arg
#'
#' @return
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

#' Match to multiple values in a function's argument
#'
#' @param arg
#'
#' @return
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
#' @return
#' @export
#'
#' @examples
init_logtable <- function() {
  # Import module
  path <- system.file("python", package = "dataharvester")
  utils <- reticulate::import_from_path("utils",
    path = path,
    delay_load = TRUE
  )
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
#' @param logname
#' @param file_name
#' @param layer
#' @param source
#' @param settings
#' @param layertitles
#' @param agfunctions
#' @param loginfos
#'
#' @return
#' @export
#'
#' @examples
update_logtable <- function(logname,
                                file_name,
                                layer,
                                source,
                                settings,
                                layertitles = list(),
                                agfunctions = list(),
                                loginfos = list()) {
  # Import module
  path <- system.file("python", package = "dataharvester")
  utils <- reticulate::import_from_path("utils",
    path = path,
    delay_load = TRUE
  )
  # Run
  out <- utils$update_logtable(df_log,
    filenames,
    layernames,
    datasource,
    settings,
    layertitles,
    agfunctions,
    loginfos)
  return(out)
}


