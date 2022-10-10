"""
Download landscape data from Soil and Landscape Grid of Australia (SLGA).

Core functionality:
- Retrieval of WCS capability  with function get_capabilities()
- automatic download landscape data via Web Coverage Service (WCS)
- clip data to custom bounding box
- save data as multi-band geotif
- plot data as map

The landscape layers and metadata are described as dictionary in the module function get_landscapedict()
and the respective licensing and attribution are available with the module function getdict_license()

More details about the data and attributions can be found here:
https://www.clw.csiro.au/aclep/soilandlandscapegrid/ProductDetails-LandscapeAttributes.html

This package is part of the Data Harvester project developed for the Agricultural Research Federation (AgReFed).

Copyright 2022 Sydney Informatics Hub (SIH), The University of Sydney

This open-source software is released under the LGPL-3.0 License.

Author: Sebastian Haan
"""

import os
from owslib.wcs import WebCoverageService
import rasterio
from rasterio.plot import show
import matplotlib.pyplot as plt
from termcolor import cprint, colored
from alive_progress import alive_bar, config_handler
import utils
from utils import spin


def get_landscapedict():
    """
    Get dictionary of landscape SLGA data.
    The landscape attribute products available from the Soil and Landscape Grid of Australia (SLGA)
    were derived from DEM-S, the smoothed version of the national 1 second resolution Digital Elevation Model,
    which was derived from the 1 second resolution Shuttle Radar Topography Mission (SRTM) data acquired by NASA in February 2000.

    Spatial resolution: 3 arc seconds (approx 90m);
    Data license : Creative Commons Attribution 3.0 (CC By);
    Format: GeoTIFF.

    Run function get_capabilities(url) to update dictionary

    Returns
    -------
    ldict : dictionary of National Soil Map data
    """
    ldict = {}
    ldict["title"] = "Landscape"
    ldict["description"] = "National Landscape Grid of Australia"
    ldict["crs"] = "EPSG:4326"
    ldict["bbox"] = [
        112.9995833334,
        -44.0004166670144,
        153.999583334061,
        -10.0004166664663,
    ]
    ldict["resolution_arcsec"] = 3
    ldict["layernames"] = {
        "Prescott_index": "1",
        "net_radiation_jan": "2",
        "net_radiation_july": "3",
        "total_shortwave_sloping_surf_jan": "4",
        "total_shortwave_sloping_surf_july": "5",
        "Slope": "6",
        "Slope_median_300m": "7",
        "Slope_relief_class": "8",
        "Aspect": "9",
        "Relief_1000m": "10",
        "Relief_300m": "11",
        "Topographic_wetness_index": "12",
        "TPI_mask": "13",
        "SRTM_TopographicPositionIndex": "14",
        "Contributing_area": "15",
        "MrVBF": "16",
        "Plan_curvature": "17",
        "Profile_curvature": "18",
    }
    return ldict


def getdict_license():
    """
    Retrieves the SLGA license and attribution information as dict
    """
    dict = {
        "name": "Soil and Landscape Grid of Australia (SLGA)",
        "source_url": "https://www.clw.csiro.au/aclep/soilandlandscapegrid/ProductDetails.html",
        "license": "CC BY 4.0",
        "license_title": "Creative Commons Attribution 4.0 International (CC BY 4.0)",
        "license_url": "https://creativecommons.org/licenses/by/4.0/",
        "copyright": "(c) 2010-2022 CSIRO Australia, © 2020 TERN (University of Queensland)",
        "attribution": "CSIRO Australia, TERN (University of Queensland), and Geoscience Australia",
    }
    return dict


def plot_raster(infname):
    """
    Read in raster tif with rasterio and visualise as map

    Parameters
    ----------
    infname : str
    """
    data = rasterio.open(infname)
    # show image
    show(data)


def get_capabilities():
    """
    Get capabilities from WCS layer

    Parameters
    ----------
    url : str
        layer url

    Returns
    -------
    keys    : list
        layer identifiers
    titles  : list  of str
        layer titles
    descriptions : list of str
        layer descriptions
    bboxs   : list of floats
        layer bounding boxes
    """
    url = "https://www.asris.csiro.au/arcgis/services/TERN/SRTM_attributes_3s_ACLEP_AU/MapServer/WCSServer?SERVICE=WCS&REQUEST=GetCapabilities"
    # Create WCS object
    wcs = WebCoverageService(url, version="1.0.0")

    # Get coverages and content dict keys
    content = wcs.contents
    keys = content.keys()

    print("Operations possible: ", [op.name for op in wcs.operations])

    # Get bounding boxes and crs for each coverage
    bbox_list = []
    title_list = []
    description_list = []
    for key in keys:
        print(f"key: {key}")
        print(f"title: {wcs[key].title}")
        title_list.append(wcs[key].title)
        print(f"{wcs[key].abstract}")
        description_list.append(wcs[key].abstract)
        print(f"bounding box: {wcs[key].boundingboxes}")
        bbox_list.append(wcs[key].boundingboxes)
        print("")

    return keys, title_list, description_list, bbox_list


def get_wcsmap(url, identifier, crs, bbox, resolution, outfname, layername):
    """
    Download and save geotiff from WCS layer

    Parameters
    ----------
    url : str
    identifier : str
        layer identifier
    crs : str
        layer crs
    bbox : list
        layer bounding box
    resolution : int
        layer resolution
    outfname : str
        output file name

    """
    # Create WCS object
    layer_fname = f"Landscape_{layername}.tif"
    if os.path.exists(outfname):
        utils.msg_warn(f"{layer_fname} already exists, skipping download")
    else:
        with spin(f"Downloading {layer_fname}") as s:
            wcs = WebCoverageService(url, version="1.0.0")
            # Get data
            data = wcs.getCoverage(
                identifier,
                format="GEOTIFF",
                bbox=bbox,
                crs=crs,
                resx=resolution,
                resy=resolution,
            )
            s(1)
        # Save data
        with open(outfname, "wb") as f:
            f.write(data.read())


def get_landscape_layers(layernames, bbox, outpath, resolution=3):
    """
    Download landscape layers from SLGA data server and saves as geotif.

    Parameters
    ----------
    layernames : list of layer names
    bbox : bounding box [min, miny, maxx, maxy] in
    resolution : resolution in arcsec (Default: 3 arcsec ~ 90m, which is native resolution of SLGA data)
    outpath : output path

    Returns
    -------
    fnames_out : list of output file names

    TBD: check that Request image size does not exceeds allowed limit. Set Timeout?
    """

    # Check if layernames is a list
    if not isinstance(layernames, list):
        layernames = [layernames]

    # Check if outpath exist, if not create it
    os.makedirs(outpath, exist_ok=True)

    # If the resolution passed is None, set to native resolution of datasource
    if resolution is None:
        resolution = get_landscapedict()["resolution_arcsec"]

    # Get dictionary and layer keys
    landscapedict = get_landscapedict()
    layer_keys = landscapedict["layernames"]

    # Convert resolution from arcsec to degree
    resolution_deg = resolution / 3600.0

    # set crs
    crs = "EPSG:4326"

    # URL
    url = "https://www.asris.csiro.au/arcgis/services/TERN/SRTM_attributes_3s_ACLEP_AU/MapServer/WCSServer?SERVICE=WCS"

    fnames_out = []
    # Loop over layers
    for layername in layernames:
        # Get layer key
        layerkey = layer_keys[layername]
        # Get layer name
        layer_fname = f"Landscape_{layername}.tif"
        # Layer fname
        fname_out = os.path.join(outpath, layer_fname)
        # download data
        get_wcsmap(url, layerkey, crs, bbox, resolution_deg, fname_out, layername)
        # print(f"{layername} downloaded. Saved to: ", fname_out)
        fnames_out.append(fname_out)
    return fnames_out


### test functions ###
def test_wcs():
    layernames = ["Slope", "net_radiation_jan", "Profile_curvature"]
    # define bounding box for retrieval (simple test here for ~ half of Australia)
    bbox = (130, -44, 153.9, -11)
    # define resolution (in arcsec per pixel since crs is in WGS84).
    # Note that there is a request size limit for the WCS service.
    resolution = 50
    # define output file name
    outpath = "result_landscape_test"
    # Get data for first layer depth
    fnames_out = get_landscape_layers(layernames, bbox, outpath, resolution)
    # Show data
    plot_raster(fnames_out[0])
