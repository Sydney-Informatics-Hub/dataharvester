"""
Script to download Radiometric data from NCI’s GSKY Data Server (using WCS) for a given
resolution, and bounding box. Final data is saved as geotiff or NetCDF.


A full ist of datasets can be retrieved with get_radiometricdict() or get_capabilities() for a given url
An overview of all datasets can be also found here:
https://opus.nci.org.au/display/Help/Datasets

For more details of the NCI GSKY WCS, please see here:
https://opus.nci.org.au/pages/viewpage.action?pageId=137199852


LIMITATIONS: for some layers the server readout time can occasionally exceed 30s (longer readout time in request seems to be ignored)
In case this happens please try later again when the NCI server is less loaded.

This package is part of the Data Harvester project developed for the Agricultural Research Federation (AgReFed).

Copyright 2022 Sydney Informatics Hub (SIH), The University of Sydney

This open-source software is released under the LGPL-3.0 License.

Author: Sebastian Haan

"""

import os
from owslib.wcs import WebCoverageService
import rasterio
from rasterio.plot import show
from datetime import datetime, timezone
from termcolor import cprint, colored
from alive_progress import alive_bar, config_handler
import utils
from utils import spin


def get_radiometricdict():
    """
    Returns dictionary of keys and layer titles

    To update manually please run get_capabilities() to retrieve all current layer details
    """
    rmdict = {
        "resolution_arcsec": 3.6,
        "layernames": {
            "radmap2019_grid_dose_terr_awags_rad_2019": "Radiometric Grid of Australia (Radmap) v4 2019 unfiltered terrestrial dose rate",
            "radmap2019_grid_dose_terr_filtered_awags_rad_2019": "Radiometric Grid of Australia (Radmap) v4 2019 filtered terrestrial xf",
            "radmap2019_grid_k_conc_awags_rad_2019": "Radiometric Grid of Australia (Radmap) v4 2019 unfiltered pct potassium",
            "radmap2019_grid_k_conc_filtered_awags_rad_2019": "Radiometric Grid of Australia (Radmap) v4 2019 filtered pct potassium grid",
            "radmap2019_grid_th_conc_awags_rad_2019": "Radiometric Grid of Australia (Radmap) v4 2019 unfiltered ppm thorium",
            "radmap2019_grid_th_conc_filtered_awags_rad_2019": "Radiometric Grid of Australia (Radmap) v4 2019 filtered ppm thorium",
            "radmap2019_grid_thk_ratio_awags_rad_2019": "Radiometric Grid of Australia (Radmap) v4 2019 ratio thorium over potassium",
            "radmap2019_grid_u2th_ratio_awags_rad_2019": "Radiometric Grid of Australia (Radmap) v4 2019 ratio uranium squared over thorium",
            "radmap2019_grid_u_conc_awags_rad_2019": "Radiometric Grid of Australia (Radmap) v4 2019 unfiltered ppm uranium",
            "radmap2019_grid_u_conc_filtered_awags_rad_2019": "Radiometric Grid of Australia (Radmap) v4 2019 filtered ppm uranium",
            "radmap2019_grid_uk_ratio_awags_rad_2019": "Radiometric Grid of Australia (Radmap) v4 2019 ratio uranium over potassium",
            "radmap2019_grid_uth_ratio_awags_rad_2019": "Radiometric Grid of Australia (Radmap) v4 2019 ratio uranium over thorium",
        },
    }
    return rmdict


def getdict_license():
    """
    Retrieves the Geoscience Australia data license and NCI attribution information as dict
    """
    dict = {
        "name": "Geoscience Australia National Geophysical Compilation Sub-collection Radiometrics",
        "source_url": "https://opus.nci.org.au/display/Help/Datasets",
        "license": "CC BY 4.0",
        "license_title": "Creative Commons Attribution 4.0 International (CC BY 4.0)",
        "license_url": "https://creativecommons.org/licenses/by/4.0/",
        "copyright": "© Copyright 2017-2022, Geoscience Australia",
        "attribution": "Geoscience Australia. The WCS service relies on GSKY - A Scalable, Distributed Geospatial Data Service \
from the National Centre for Environmental Information (NCI).",
    }
    return dict


def plot_raster(infname):
    """
    Read in raster tif with rasterio and visualise as map.

    Parameters
    ----------
    infname : str
    """
    data = rasterio.open(infname)
    # show image
    show(data)


def get_capabilities():
    """
    Get capabilities from WCS layer.

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

    # URL
    url = "https://gsky.nci.org.au/ows/national_geophysical_compilations?service=WCS&version=1.0.0&request=GetCapabilities"

    # Create WCS object
    wcs = WebCoverageService(url, version="1.0.0", timeout=300)

    # Get coverages and content dict keys
    content = wcs.contents
    keys = content.keys()

    print("Following data layers are available:")
    title_list = []
    description_list = []
    bbox_list = []
    for key in keys:
        print(f"key: {key}")
        print(f"title: {wcs[key].title}")
        title_list.append(wcs[key].title)
        print(f"{wcs[key].abstract}")
        description_list.append(wcs[key].abstract)
        print(f"bounding box: {wcs[key].boundingBoxWGS84}")
        bbox_list.append(wcs[key].boundingBoxWGS84)
        print("")

    return keys, title_list, description_list, bbox_list


def get_radiometric_layers(
    outpath, layernames, bbox, resolution=1, crs="EPSG:4326", format_out="GeoTIFF"
):
    """
    Wrapper function for downloading radiometric data layers and save geotiffs from WCS layer.

    Parameters
    ----------
    outpath: str
        output path
    layername : list of strings
        layer identifiers
    bbox : list
        layer bounding box
    resolution : int
        layer resolution in arcsec
    url : str
        url of wcs server
    crs: str
        crsm default 'EPSG:4326'
    format_out: str
        output format, either "GeoTIFF" or "NetCDF"

    Return
    ------
    list of output filenames
    """
    url = "https://gsky.nci.org.au/ows/national_geophysical_compilations?service=WCS"
    if type(layernames) != list:
        layernames = [layernames]
    if format_out == "GeoTIFF":
        fname_end = ".tif"
    elif format_out == "NetCDF":
        fname_end = ".nc"
    else:
        print(f"\u2716 {format_out} not supported. Choose either GeoTIFF or NetCDF.")
        return outfnames

    # Loop over all layers
    fnames_out = []
    for layername in layernames:
        outfname = os.path.join(outpath, "radiometric_" + layername + fname_end)
        ok = get_radiometric_image(
            outfname, layername, bbox, url, resolution=1, crs=crs, format_out=format_out
        )
        if ok:
            fnames_out.append(outfname)
    return fnames_out


def get_radiometric_image(
    outfname, layername, bbox, url, resolution=1, crs="EPSG:4326", format_out="GeoTIFF"
):
    """
    Download radiometric data layer and save geotiff from WCS layer.

    Parameters
    ----------
    outfname : str
        output file name
    layername : str
        layer identifier
    bbox : list
        layer bounding box
    resolution : int
        layer resolution in arcsec
    url : str
        url of wcs server
    crs: str
        crsm default 'EPSG:4326'
    format: str
        output format, either "GeoTIFF" or "NetCDF"

    Return
    ------
    Exited ok: boolean
    """
    # If the resolution passed is None, set to native resolution of datasource
    if resolution is None:
        resolution = get_radiometricdict()["resolution_arcsec"]

    # Convert resolution into width and height pixel number
    width = abs(bbox[2] - bbox[0])
    height = abs(bbox[3] - bbox[1])
    nwidth = int(width / resolution * 3600)
    nheight = int(height / resolution * 3600)
    # Get date
    times = get_times(url, layername)
    # There is only one time available per layer
    date = times[0]
    # Get data
    if os.path.exists(outfname):
        utils.msg_warn(f"{layername}.tif already exists, skipping download")
    else:
        try:
            with spin(f"Downloading {layername}") as s:
                wcs = WebCoverageService(url, version="1.0.0", timeout=300)
                data = wcs.getCoverage(
                    identifier=layername,
                    time=[date],
                    bbox=bbox,
                    format=format_out,
                    crs=crs,
                    width=nwidth,
                    height=nheight,
                )
                s(1)
        except:
            utils.msg_err("Download failed")
            return False

        # Save data
        with open(outfname, "wb") as f:
            f.write(data.read())
        # print(f"Layer {layername} saved in {outfname}")
    return True


def get_times(url, layername, year=None):
    """
    Return available dates for layer.

    Parameters
    ----------
    url: str, layer url
    layername: str, name of layer id
    year: int or str, year of interest (if None, times for all available years are returned)

    Return
    ------
    list of dates
    """
    wcs = WebCoverageService(url, version="1.0.0", timeout=300)
    times = wcs[layername].timepositions
    if year is None:
        return times
    else:
        year = int(year)
        dates = []
        for time in times:
            if datetime.fromisoformat(time[:-1]).astimezone(timezone.utc).year == year:
                dates.append(time)
        return dates


### Some test functions ###


def test_get_capabilities():
    """
    Test script to retrieve WCS capabilities
    """
    # Get capabilities
    keys, titles, descriptions, bboxs = get_capabilities()
    assert len(keys) > 0


def test_get_times():
    """
    Test script to retrieve available times for a layer
    """
    url = "https://gsky.nci.org.au/ows/national_geophysical_compilations?service=WCS"
    times = get_times(url, layername)
    assert len(times) > 0


def test_times():
    """
    Check that there is only one time per layers.
    """
    url = "https://gsky.nci.org.au/ows/national_geophysical_compilations?service=WCS"
    radiometricdict = get_radiometricdict()
    layernames = radiometricdict["layernames"]
    for key in layernames:
        times = get_times(url, key)
        print(f"{key}: {times}")
        assert len(times) == 1


def test_get_radiometric_image():
    """
    Test script to retrieve and save image for one layer
    """
    url = "https://gsky.nci.org.au/ows/national_geophysical_compilations?service=WCS"
    layername = "radmap2019_grid_dose_terr_filtered_awags_rad_2019"  # "radmap2019_grid_dose_terr_awags_rad_2019"  # for some layers readout time of 30s is exceeding (server limited)
    crs = "EPSG:4326"  # WGS84
    # define bounding box for retrieval (simple test here for entire Australia)
    bbox = (114, -44, 153.9, -11)
    # define resolution (in arcsecs per pixel since crs is in WGS84)
    resolution = 100
    # define output file name
    fname_out = f"test_{layername}.tif"
    # Get data
    download_ok = get_radiometric_image(
        fname_out, layername, bbox, url, resolution=resolution
    )
    assert download_ok
