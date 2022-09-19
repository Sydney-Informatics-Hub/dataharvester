
<!-- README.md is generated from README.Rmd. Please edit that file -->
<!-- badges: start -->
<!-- badges: end -->

<img src="man/figures/logo_r.png" width="300" style="display: block; margin: auto;" />

`dataharvester` is an R interface to the AgReFed Data Harvester. Use
`dataharvester` to preprocess, aggregate, visualise and download
geospatial data from a range of Australian and international data
sources, including:

-   [Soil and Landscape Grid of Australia (SLGA)](https://is.gd/i8nF0Z)
-   [SILO Climate Database](https://is.gd/ifJ8tB)
-   [Digital Elevation Model (DEM) of Australia](https://is.gd/ZLFwGs)
-   [Digital Earth Australia (DEA) Geoscience Earth
    Observations](https://is.gd/gRSlVG)
-   [GSKY Data Server for DEA Geoscience Earth
    Observations](https://is.gd/zFHxfD)
-   [Google Earth Engine](https://is.gd/VdO3Jx)

With connectivity to the Earth Engine API, perform petabyte-scale
operations which include temporal cloud/shadow masking and automatic
calculation of spectral indices (e.g. NDVI) for the following
collections:

-   Landsat
    [5](https://developers.google.com/earth-engine/datasets/catalog/landsat-5)
    (TM),
    [7](https://developers.google.com/earth-engine/datasets/catalog/landsat-7)
    (ETM+),
    [8](https://developers.google.com/earth-engine/datasets/catalog/landsat-8)
    (OLI/TRS) and
    [9](https://developers.google.com/earth-engine/datasets/catalog/landsat-9)
    (OLI-2/TRS-2)
-   [Sentinel-2](https://developers.google.com/earth-engine/datasets/catalog/sentinel-2)
    (Surface Reflectance) and
    [Sentinel-3](https://developers.google.com/earth-engine/datasets/catalog/COPERNICUS_S3_OLCI)
    (Ocean and Land Colour Instrument)
-   [MODIS](https://developers.google.com/earth-engine/datasets/catalog/modis)
    (or Moderate Resolution Imaging Spectroradiometer) products

For [all other Earth Engine
collections](https://developers.google.com/earth-engine/datasets/),
while `dataharvester` does not provide officual support, users can still
perform basic operations to filter, reduce, visualise and download data.

## Installation

**Important: `dataharvester` is currently still under early development.
Do not download this package unless you are a developer and love to
break things.**

Install the development version of this package from GitHub using
`install_github()` from `remotes` or `devtools`:

``` r
# install.packages("remotes") # uncomment and run this line if necessary
remotes::install_github("Sydney-Informatics-Hub/dataharvester")

library(dataharvester) # load package
```

## Examples

### “Headless” run

Run `initialise_harvester()` after loading the package. The function
helps you initialise the package, verifies package dependencies and
connect to the Earth Engine API.

``` r
library(dataharvester)
initialise_harvester(earthengine = TRUE)
```

Then, run `harvest()`, which parses a YAML config file:

``` r
harvest("path/to/config.yaml")
```

### Manual downloads

``` r
# TODO
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

We would also like to acknowledge the use of the following Python
packages in `dataharvester`:

-   [geemap](https://github.com/giswqs/geemap)
-   [wxee](https://github.com/aazuspan/wxee)
-   [eemont](https://github.com/davemlz/eemont)

## License

Copyright 2022 The University of Sydney

This is free software: you can redistribute it and/or modify it under
the terms of the GNU Lesser General Public License (LGPL version 3) as
published by the Free Software Foundation.
