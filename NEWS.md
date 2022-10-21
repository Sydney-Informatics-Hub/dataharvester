# dataharvester 0.0.15

In this release we fixed a few bugs and added several vignettes for the various download functions.

### What's changed

- fixed relative path strings not being recognised by Python modules in `harvest()`
- added a demo .gif to README so that readers can preview functionality

### What's new

- created 5 new vignettes to document layers available for downloading from the various data sources

# dataharvester 0.0.14

This release focuses on data extraction from rasters and plot functions that should "simply work". We also started to implement unit testing as the package code contains *some* R code.

### What's changed

- improved message outputs when using download functions. This was important as there was some overlap between Python and R message and print outputs. This update makes the feedback (to the user) less verbose and more consistent and prepares the package for a better logging feature (which will be finalise in a future update)
- the folder path can now be retrieved directly from an object produced by `download_ee()`, which is useful for plotting and other data manipulation functions which rely on extracting data from a downloaded GeoTIFF file

### What's new

- `plot()` for `download_*()` objects, thanks to the `terra` package
- `extract_values()` to extract values from GeoTIFF files
- started to implement unit testing for some functions with `testthat`

# dataharvester 0.0.13

Another quick bugfix release.

### What's changed

- authenticating to GEE in RStudio Cloud is now more reliable when running `initialise_harvester()` as we have added an argument `auth_mode` to manually set the authentication method

# dataharvester 0.0.12

This is a quick bugfix release.

### What's changed

- fixed an error in `harvest()` that can occur when the `infile` attribute exists but contains no path, leading the function to incorrectly think that sampling data exists

# dataharvester 0.0.11

### What's changed

- implemented slightly better console feedback when downloading data (on Python side)
- `plot_rasters()`: fixed plotting issue when only one raster is in folder

### What's new

- S3 `plot()` methods now available with `download_*()` functions

# dataharvester 0.0.10

This version updates the package Python modules. There are no major changes to the R code.

### What's changed

- Messages imported from Python are a bit more organised (more to improve in a later version, but these are cosmetic changes)
- `download_dem()`: arguments were not ordered like other similar functions, so we adjusted this
- Better support for YAML config files (especially when some attributes are missing)

# dataharvester 0.0.9

A fix to achieve reliable Python module imports (hopefully).

### What's changed

- All functions that import Python modules point directly to the `.py` files, instead of the python folder. Hopefully fixes an internal testing error of `"module not found"`

### What's new
- `raster_query()` samples one or more rasters based on existing sampling data to generate a sampling file of point-specifig geospatial information from all images


# dataharvester 0.0.8

Big focus on making sure that dependencies work, as well as making sure that YAML config file processing workflow is more reproducible.

### What's changed

- improved 'harvest()` for abilities to change the output download log name and plot rasters in a folder
- `initialise_harvester()` can now create other environments, not just stick to `r-reticulate`
- fixed errors in installing google cloud sdk on Windows machines


### What's new
- `plot_rasters()` function to scan a folder recursively and plot the first band of all GeoTIFF images
- `create_yaml()` function to generate template and skeleton YAML files. The function is incomplete, but it will be finalised in the next version
- fixed encoding and missing link errors in documentation (#7)
- fixed conda openSSL error (#8)

# dataharvester 0.0.7

Another quick update to fix issues with Google Earth Engine authentication.



# dataharvester 0.0.6

A quick update to authentication methods for Google Earth Engine (fingers crossed).

### What's changed:

- 🛠: Changed how `intialise_harvester()` works with Google Earth Engine to be more compatible with RStudio Cloud/Binder.


# dataharvester 0.0.5

This version focuses on more download options and improved validation to Python dependencies and Google Earth Engine.

### What's new:

- ⚡: `download_dea()` for Digital Earth Australia downloads
- ⚡: `download_landscape()` for SLGA Landscape products
- ⚡: `download_radiometric()` for Geoscience Australia Radiometric maps
- ⚡: `download_silo()` now accepts more than 1 layer for downloads


### What's changed:

- 🛠: Config/reticulate is no longer used to validate Python dependencies, since different package versions needed to be installed depending on the workspace environment (i.e. RStudio Desktop, RStudio Cloud, or Binder).
- 🏎: performance and usability improvements to `initialise_harvester()`

# dataharvester 0.0.4

This is mainly a bugfix 🪲 (and some testing) release with no new features.

# dataharvester 0.0.3

### What's new:

- ⚡: `add_silo()` for climate SILO downloads, not working 100% 😢
- 📰: added examples to README


# dataharvester 0.0.2

General bug fixes, added new functions that will someday replace `get_*()` functions.

### What's new: 

- ⚡: `init_logtable()` and `update_logtable()` to store download info
- ⚡: `download_slga()` to download from SLGA
- ⚡: `download_dem()` to download from DEM
- ⚡: `match_single()` and `match_multi()` to validate args
- ⚡: `load_setttings()` to read YAML file 
- 🛠: added CI to automate pkgdown deployment

### What's changed:

- 🪲: `ee_map()` was not presenting map on RStudio viewer - fixed by switching to `geemap.foliummap`
- 🔁: renamed `ee_*()` functions to `*_ee()` for consistency
- 🏎: performance upgrades to `initialise_harvester()`
- ⬆️️: updated Python dependencies including imports and `.py` files

# dataharvester 0.0.1

This update will only describe package features as no one would have had the chance to report bugs.


- `initialise_harvester()` which checks for Python depends and authentitcates Earth Engine
- `ee_collect()` which generates an object for Earth Engine processing and downlaods
- `ee_preprocess()` to perform masking, filtering, spectral index calculations and scaling
- `ee_aggregate()` for basic temporal aggregation of images
- `ee_map()` to visualise Earth Engine images on an interactive map
- `harvest()` to perform "headless" data harvesting when paired with a config YAML
- `get_slga()` for SLGA downloads
- `get_dea()` for DEA downloads
- Some initial documentation has been added to functions, but most are draft-y
- `README.md` has been added
- Initial `pkgdown` support added, but cannot be tested yet since repo is not public

# dataharvester 0.0.0.9000

* Added a `NEWS.md` file to track changes to the package.
