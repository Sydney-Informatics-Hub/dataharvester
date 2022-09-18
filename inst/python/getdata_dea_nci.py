"""
Script to download satellite data from NCI’s GSKY Data Server (uisng WCS) for a given time,
resolution, and bounding box. Final data is saved as geotiff or NetCDF.

Satellite data sources are calibrated with Digital Earth Australia (DEA) and include datasets for Landsat and Sentinel2.

A full ist of datasets can be retrieved with get_deadict() or get_capabilities() for a given url
An overview of all datasets can be also found here:
https://opus.nci.org.au/display/Help/Datasets

For more details of the NCI GSKY WCS, please see here:
https://opus.nci.org.au/pages/viewpage.action?pageId=137199852

An alternative WCS service is available at:
https://docs.dea.ga.gov.au/setup/gis/web_services.html#Web-Coverage-Service-(WCS)

LIMITATIONS: for some layers the server readout time can occasionally exceed 30s (longer readout time in request seems to be ignored)
In case this happens please try later again when the NCI server is less loaded.


This package is part of the Data Harvester project developed for the Agricultural Research Federation (AgReFed).

Copyright 2022 Sydney Informatics Hub (SIH), The University of Sydney

This open-source software is released under the LGPL-3.0 License.

Author: Sebastian Haan

TBD:
- change WCS source that includes multiple bands with cloud masks

"""

import os
from owslib.wcs import WebCoverageService
import rasterio
from rasterio.plot import show
from datetime import datetime, timezone

# logger setup
import write_logs
import logging


def get_deadict():
    """
    Returns dictionary of keys and layer titles

    To update manually please run get_capabilities() to retrieve all current layer details
    """
    deadict = {
        "resolution_arcsec": 1,
        "layernames": {
            "blend_sentinel2_landsat_nbart_daily": "Multi-sensor (Landsat and Sentinel 2) surface reflectance (Beta)",
            "hltc_high": "DEA High Tide Composite 25m v2.0",
            "hltc_low": "DEA Low Tide Composite 25m v2.0",
            "item_relative": "DEA Intertidal Extents Model Relative Layer 25m v2.0",
            "item_stddev": "DEA Intertidal Extents Model Confidence Layer 25m v2.0",
            "landsat5_nbar_16day": "16-day DEA Landsat 5 surface reflectance",
            "landsat5_nbar_daily": "Daily DEA Landsat 5 surface reflectance",
            "landsat5_nbart_16day": "16-day DEA Landsat 5 terrain corrected surface reflectance",
            "landsat5_nbart_daily": "Daily DEA Landsat 5 terrain corrected surface reflectance",
            "landsat7_nbar_16day": "16-day DEA Landsat 7 surface reflectance",
            "landsat7_nbar_daily": "Daily DEA Landsat 7 surface reflectance",
            "landsat7_nbart_16day": "16-day DEA Landsat 7 terrain corrected surface reflectance",
            "landsat7_nbart_daily": "Daily DEA Landsat 7 terrain corrected surface reflectance",
            "landsat8_nbar_16day": "16-day DEA Landsat 8 surface reflectance",
            "landsat8_nbar_daily": "Daily DEA Landsat 8 surface reflectance",
            "landsat8_nbart_16day": "16-day DEA Landsat 8 terrain corrected surface reflectance",
            "landsat8_nbart_daily": "Daily DEA Landsat 8 terrain corrected surface reflectance",
            "sentinel2_nbart_daily": "Sentinel 2 Analysis Ready Data",
            "wofs": "DEA Water Observation Feature Layer",
        },
    }
    return deadict


def getdict_license():
    """
    Retrieves the DEA data license and NCI attribution information as dict
    """
    dict = {
        "name": "Digital Earth Australia (DEA) Geoscience Earth Observations",
        "source_url": "https://opus.nci.org.au/display/Help/Datasets",
        "license": "CC BY 4.0",
        "license_title": "Creative Commons Attribution 4.0 International (CC BY 4.0)",
        "license_url": "https://creativecommons.org/licenses/by/4.0/",
        "copyright": "© Copyright 2017-2022, Geoscience Australia",
        "attribution": " The data products are produced using Digital Earth Australia. \
The WCS service relies on GSKY - A Scalable, Distributed Geospatial Data Service \
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


def get_capabilities(url):
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


def get_wcsmap(
    outfname,
    layername,
    bbox,
    date,
    url,
    resolution=1,
    crs="EPSG:4326",
    format_out="GeoTIFF",
):
    """
    Download and save geotiff from WCS layer.

    Parameters
    ----------
    outfname : str
        output file name
    layername : str
        layer identifier
    bbox : list
        layer bounding box
    date : str
        datetime
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
        resolution = get_deadict()["resolution_arcsec"]

    # Convert resolution into width and height pixel number
    width = abs(bbox[2] - bbox[0])
    height = abs(bbox[3] - bbox[1])
    nwidth = int(width / resolution * 3600)
    nheight = int(height / resolution * 3600)
    # Get data
    if os.path.exists(outfname):
        logging.print(f"△ | download skipped: {outfname} already exists")
    else:
        try:
            wcs = WebCoverageService(url, version="1.0.0", timeout=300)
            data = wcs.getCoverage(
                identifier=layername,
                time=[date],
                bbox=bbox,
                format=format_out,
                crs=crs,
                width=nwidth,
                height=nheight,
                Styles="tc",
            )
        except:
            print("Download failed")
            return False

        # Save data
        with open(outfname, "wb") as f:
            f.write(data.read())
    return True


def get_dea_images(
    layername,
    year,
    bbox,
    outpath,
    resolution=1,
    crs="EPSG:4326",
    format_out="GeoTIFF",
    verbose=False,
):
    """
    Get all satellite images from DEA for a given layer and year.
    Downloaded images are saved either as GeoTIFF or NetCDF.

    Parameters
    ----------
    layername : str
        layer identifier
    year : str
        selected year fpor images
    bbox : list
        layer bounding box
    resolution : int
        layer resolution in arcsec
    outpath : str
        output directory
    crs: str
        crs, default 'EPSG:4326'
    format: str
        output format, either "GeoTIFF" or "NetCDF"

    Return
    ------
    Exited ok: boolean
    """
    # Logger setup
    if verbose:
        write_logs.setup(level="info")
    else:
        write_logs.setup()

    os.makedirs(outpath, exist_ok=True)

    # If the resolution passed is None, set to native resolution of datasource
    if resolution is None:
        resolution = get_deadict()["resolution_arcsec"]

    # URL
    url = "https://gsky.nci.org.au/ows/dea?service=WCS&version=1.0.0&request=GetCapabilities"

    # Check if layername is defined
    dict_dea = get_deadict()
    if layername not in dict_dea["layernames"]:
        logging.print(f"{layername} not a DEA layer. Check log for suggestions")
        logging.info(
            f"{layername} not a DEA layer. Please select one of the following:"
        )
        for key in dict_dea:
            logging.info(key)

    # Get available timecoverage
    try:
        times = get_times(url, layername)
    except Exception as e:
        logging.error(f"Exception in timecoverage request with error {e}")
        return False

    # Convert times to datetime and select dates that are within the choosen year
    datetimes = []
    dates = []
    year = int(year)
    for time in times:
        if datetime.fromisoformat(time[:-1]).astimezone(timezone.utc).year == year:
            datetimes.append(datetime.fromisoformat(time[:-1]).astimezone(timezone.utc))
            dates.append(time)
    logging.print(f"Number of images for {year} found: {len(dates)}")
    if len(dates) == 0:
        logging.error(f"No dates found for year {year}")
        return False

    # Download images for all dates in year
    for date in dates:
        if format_out == "GeoTIFF":
            fname_end = ".tif"
        elif format_out == "NetCDF":
            fname_end = ".nc"
        else:
            logging.error(
                f"{format_out} not supported. Choose either GeoTIFF or NetCDF."
            )
            return False
        datestring = datetime.fromisoformat(date[:-1]).astimezone(timezone.utc)
        fname_out = f"{layername}_{datestring.year}-{datestring.month}-{datestring.day}{fname_end}"
        outfname = os.path.join(outpath, fname_out)
        # Get data
        logging.info(f"Downloading {layername} for date {date} ...")
        download_ok = get_wcsmap(
            outfname,
            layername,
            bbox,
            date,
            url,
            resolution=resolution,
            crs=crs,
            format_out=format_out,
        )
    logging.print(f"All image downloads can be found in {outpath}.")
    return True


### Some test functions ###


def test_get_capabilities():
    """
    Test script to retrieve WCS capabilities
    """
    # DEA layer
    url = "https://gsky.nci.org.au/ows/dea?service=WCS&version=1.0.0&request=GetCapabilities"
    # Get capabilities
    keys, titles, descriptions, bboxs = get_capabilities(url)
    assert len(keys) > 0


def test_get_times():
    """
    Test script to retrieve available times for a layer
    """
    url = "https://gsky.nci.org.au/ows/dea?service=WCS"
    times = get_times(url, layername)
    assert len(times) > 0


def test_get_wcsmap():
    """
    Test script to retrieve and save image for one layer and date
    """
    url = "https://gsky.nci.org.au/ows/dea?service=WCS"
    layername = "landsat8_nbart_16day"  # "sentinel2_nbart_daily" # for some layers readout time of 30s is exceeding (server limited)
    times = get_times(url, layername)
    crs = "EPSG:4326"  # WGS84
    # define bounding box for retrieval (simple test here for entire Australia)
    bbox = (114, -44, 153.9, -11)
    # define resolution (in arcsecs per pixel since crs is in WGS84)
    resolution = 100
    # get latest image
    time = times[-1]
    # define output file name
    fname_out = f"test_{layername}_{time}.tif"
    # Get data
    download_ok = get_wcsmap(
        fname_out, layername, bbox, time, url, resolution=resolution
    )
    assert download_ok


def test_get_dea_images():
    """
    Test script to retrieve and save images for a given year
    """
    url = "https://gsky.nci.org.au/ows/dea?service=WCS"
    # Get data (here only for first layer)
    layername = "landsat8_nbart_16day"  # "sentinel2_nbart_daily" # for some layers readout time of 30s is exceeding (server limited)
    # layername = 'sentinel2_nbart_daily'
    crs = "EPSG:4326"  # WGS84
    # define bounding box for retrieval (simple test here for entire Australia)
    bbox = (114, -44, 153.9, -11)
    # define resolution (in arcsecs per pixel since crs is in WGS84)
    resolution = 100
    # define year
    year = 2021
    # define outpath
    outpath = "test_dea"
    # Get data
    download_ok = get_dea_images(layername, year, bbox, outpath, resolution=resolution)
    assert download_ok
