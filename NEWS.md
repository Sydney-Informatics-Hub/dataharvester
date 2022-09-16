# dataharvester 0.0.1

This update will only describe package features as no one would have had the chance to report bugs.

## Features

- `initialise_harvester()` which checks for Python depends and authentitcates Earth Engine
- `ee_collect()` which generates an object for Earth Engine processing and downlaods
- `ee_preprocess()` to perform masking, filtering, spectral index calculations and scaling
- `ee_aggregate()` for basic temporal aggregation of images
- `ee_map()` to visualise Earth Engine images on an interactive map
- `harvest()` to perform "headless" data harvesting when paired with a config YAML
- `get_slga()` for SLGA downloads
- `get_dea()` for DEA downloads

## Documentation

- Some initial documentation has been added to functions, but most are draft-y
- `README.md` has been added
- Initial `pkgdown` support added, but cannot be tested yet since repo is not public

# dataharvester 0.0.0.9000

* Added a `NEWS.md` file to track changes to the package.
