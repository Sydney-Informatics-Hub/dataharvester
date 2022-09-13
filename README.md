
<!-- README.md is generated from README.Rmd. Please edit that file -->
<!-- badges: start -->

[![Codacy
Badge](https://app.codacy.com/project/badge/Grade/e715df42acef461bac6f4e0d6ba8181b)](https://www.codacy.com?utm_source=github.com&utm_medium=referral&utm_content=januarharianto/dataharvestR&utm_campaign=Badge_Grade)
<!-- badges: end -->

<img src="man/figures/logo_r.png" width="300" style="display: block; margin: auto;" />

`dataharvester` is an R interface to the [AgReFed Data Harvester](). Use
`dataharvester` to preprocess, aggregate, visualise and download
geospatial data from a range of Australian and international data
sources, including:

-   [Soil and Landscape Grid of Australia (SLGA)]()
-   [SILO Climate Database]()
-   [Digital Elevation Model (DEM) of Australia]()
-   [Digital Earth Australia (DEA) Geoscience Earth Observations]()
-   [GSKY Data Server for DEA Geoscience Earth Observations]()
-   [Google Earth Engine]()

With connectivity to the Earth Engine API, perform petabyte-scale
operations which include temporal cloud/shadow masking and automatic
calculation of spectral indices (e.g. NDVI) for the following
collections:

-   Landsat [5]() (TM), [7]() (ETM+), [8]() (OLI/TRS) and [9]()
    (OLI-2/TRS-2)
-   [Sentinel-2]() (Surface Reflectance) and [Sentinel-3]() (Ocean and
    Land Colour Instrument)
-   [MODIS](https://developers.google.com/earth-engine/datasets/catalog/modis)
    (or Moderate Resolution Imaging Spectroradiometer) products

For [all other Earth Engine
collections](https://developers.google.com/earth-engine/datasets/),
while `dataharvester` does not provide officual support, users can still
perform basic operations to filter, reduce, visualise and download data.

## Installation

Download the development version of this package from GitHub using
`install_github()`:

``` r
# install.packages("remotes") # uncomment and run this line if necessary
remotes::install_github("januarharianto/dataharvester")

library(dataharvester) # load package
```

## `initialise()`

The heart *and* soul of `dataharvester`, `intialise()` helps you
initialise the package, verifies package dependencies and connect to the
Earth Engine API. The [online documentation]() provides a detailed
outlook on what the function does.

## Example

``` r
# library(dataharvester)
# initialise(earthengine = TRUE)

# todo
```

## Acknowledgments

Acknowledgements are an important way for us to demonstrate the value we
bring to your research. Your research outcomes are vital for ongoing
funding of the Sydney Informatics Hub. If you make use of this software
for your research project, please include the following acknowledgement:

> “This research was supported by the Sydney Informatics Hub, a Core
> Research Facility of the University of Sydney, and the Agricultural
> Research Federation (AgReFed).”

# Attribution

This software was developed by the Sydney Informatics Hub, a core
research facility of the University of Sydney, as part of the Data
Harvesting project for the Agricultural Research Federation (AgReFed).
AgReFed is supported by the Australian Research Data Commons (ARDC) and
the Australian Government through the National Collaborative Research
Infrastructure Strategy (NCRIS).

## License

Copyright 2022 The University of Sydney

This is free software: you can redistribute it and/or modify it under
the terms of the GNU Lesser General Public License (LGPL version 3) as
published by the Free Software Foundation.
