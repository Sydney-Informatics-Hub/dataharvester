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
