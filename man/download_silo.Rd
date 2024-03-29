% Generated by roxygen2: do not edit by hand
% Please edit documentation in R/silo.R
\name{download_silo}
\alias{download_silo}
\title{Download from SILO database}
\usage{
download_silo(
  layer,
  bounding_box,
  out_path,
  years,
  format_out = "tif",
  delete_temp = FALSE
)
}
\arguments{
\item{layer}{Layer name(s) to download as a vector of strings}

\item{bounding_box}{A numeric vector of coordinate values used to generate a bounding box around are of interest in EPSG:4326 format, for example, \code{c(min_x, min_y, max_x, max_y)}}

\item{out_path}{Path to an output/download folder, e.g. \code{'downloads/'}}

\item{date_min}{\code{string} Start date to download in YYYY-MM-DD, e.g. \code{2019-10-01}}

\item{date_max}{\code{string} End date to download in YYYY-MM-DD, e.g. \code{2019-11-01}}

\item{format_out}{Exported file format. Only \code{"tif"} is currently available.
Defaults to \code{"tif"}}

\item{delete_temp}{Delete any temporary files that were created. Defaults to
\code{FALSE}}
}
\value{
a list of filenames (after files have been downloaded or processed)
}
\description{
Download from SILO database
}
