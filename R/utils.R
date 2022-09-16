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
