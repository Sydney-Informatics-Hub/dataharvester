#' Join path
#' @noRd
.joinpath <- function(...) {
  sep <- .Platform$file.sep
  result <- gsub(paste0(sep, "{2,}"), sep, file.path(...),
    fixed = FALSE,
    perl = TRUE
  )
  result <- gsub(paste0(sep, "$"), "", result, fixed = FALSE, perl = TRUE)
  return(result)
}
