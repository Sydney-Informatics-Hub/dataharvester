"""
Script to download satellite data from Digital Earth Australia (DEA)for a given time,
resolution, and bounding box. Final data is saved as geotiff or NetCDF.

Satellite data sources are calibrated by DEA for Australia and include datasets for Landsat and Sentinel2.

An overview of DEA data is available here
https://docs.dea.ga.gov.au/notebooks/DEA_datasets/README.html
and explanation of datasets here:
https://docs.dea.ga.gov.au/notebooks/Beginners_guide/02_DEA.html

A full ist of data layer names can be retrieved with get_deadict() or get_capabilities() for a given url
The DEA WCS service capabilities are also available online at:
https://docs.dea.ga.gov.au/setup/gis/web_services.html#Web-Coverage-Service-(WCS)

For more complex data processing use DEA's excellent Jupyter notebooks within their Sandbox (authentication needed)
that leverage the Open Data Cube software package (datacube-core)
https://docs.dea.ga.gov.au/setup/Sandbox/sandbox.html

Other resources:
- NCI (authentication needed)
https://docs.dea.ga.gov.au/setup/NCI/README.html

- SpatioTemporal Asset Catalog (STAC) endpoint  (authentication needed):
https://docs.dea.ga.gov.au/notebooks/Frequently_used_code/Downloading_data_with_STAC.html

LIMITATIONS: for large bbox the server can exceeds limits and the data is not returned.

This package is part of the Data Harvester project developed for the Agricultural Research Federation (AgReFed).

Copyright 2022 Sydney Informatics Hub (SIH), The University of Sydney

This open-source software is released under the LGPL-3.0 License.

Author: Sebastian Haan


TBF:
- apply cloud mask to downloaded images automatically (accept "valid", "water", "snow")
- include some DEA tools https://github.com/GeoscienceAustralia/dea-notebooks/blob/stable/Tools/dea_tools/

"""

import os
from owslib.wcs import WebCoverageService
import rasterio
from rasterio import MemoryFile
from rasterio.plot import show
from datetime import datetime, timezone
from termcolor import cprint, colored
import utils
from utils import spin

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
            "ga_ls_ard_3": "DEA Surface Reflectance (Landsat)",
            "s2_nrt_granule_nbar_t": "DEA Surface Reflectance (Sentinel-2 Near Real-Time)",
            "s2_ard_granule_nbar_t": "DEA Surface Reflectance (Sentinel-2)",
            "ga_ls8c_nbart_gm_cyear_3": "DEA GeoMAD (Landsat 8 OLI-TIRS)",
            "ga_ls7e_nbart_gm_cyear_3": "DEA GeoMAD (Landsat 7 ETM+)",
            "ga_ls5t_nbart_gm_cyear_3": "DEA GeoMAD (Landsat 5 TM)",
            "ga_ls8c_ard_3": "DEA Surface Reflectance (Landsat 8 OLI-TIRS)",
            "ga_ls7e_ard_3": "DEA Surface Reflectance (Landsat 7 ETM+)",
            "ga_ls5t_ard_3": "DEA Surface Reflectance (Landsat 5 TM)",
            "ga_ls8c_ard_provisional_3": "DEA Surface Reflectance (Landsat 8 OLI-TIRS, Provisional)",
            "ga_ls7e_ard_provisional_3": "DEA Surface Reflectance (Landsat 7 ETM+, Provisional)",
            "ga_ls_ard_provisional_3": "DEA Surface Reflectance (Landsat, Provisional)",
            "s2b_nrt_granule_nbar_t": "DEA Surface Reflectance (Sentinel-2B MSI Near Real-Time)",
            "s2a_nrt_granule_nbar_t": "DEA Surface Reflectance (Sentinel-2A MSI Near Real-Time)",
            "s2_nrt_provisional_granule_nbar_t": "DEA Surface Reflectance (Sentinel-2, Provisional)",
            "s2b_nrt_provisional_granule_nbar_t": "DEA Surface Reflectance (Sentinel-2B MSI, Provisional)",
            "s2a_nrt_provisional_granule_nbar_t": "DEA Surface Reflectance (Sentinel-2A MSI, Provisional)",
            "s2a_ard_granule_nbar_t": "DEA Surface Reflectance (Sentinel-2A MSI)",
            "s2b_ard_granule_nbar_t": "DEA Surface Reflectance (Sentinel-2B MSI)",
            "ga_ls_landcover": "DEA Land Cover Calendar Year (Landsat)",
            "ga_ls_landcover_descriptors": "DEA Land Cover Environmental Descriptors",
            "ga_ls_fc_3": "DEA Fractional Cover (Landsat)",
            "ga_ls_fc_pc_cyear_3": "DEA Fractional Cover Percentiles Calendar Year (Landsat)",
            "ga_ls_mangrove_cover_cyear_3": "DEA Mangroves (Landsat)",
            "s2_barest_earth": "GA Barest Earth (Sentinel-2)",
            "ls8_barest_earth_mosaic": "GA Barest Earth (Landsat 8 OLI/TIRS)",
            "landsat_barest_earth": "GA Barest Earth (Landsat)",
            "ga_ls_tcw_percentiles_2": "DEA Wetness Percentiles (Landsat)",
            "ga_ls_tc_pc_cyear_3": "DEA Tasseled Cap Indices Percentiles Calendar Year (Landsat)",
            "ga_ls_wo_3": "DEA Water Observations (Landsat)",
            "ga_ls_wo_fq_myear_3": "DEA Water Observations Multi Year (Landsat)",
            "ga_ls_wo_fq_cyear_3": "DEA Water Observations Calendar Year (Landsat)",
            "ga_ls_wo_fq_apr_oct_3": "DEA Water Observations April to October (Landsat)",
            "ga_ls_wo_fq_nov_mar_3": "DEA Water Observations November to March (Landsat)",
            "wofs_filtered_summary": "DEA Multi-Year Water Observation Frequency Filtered Statistics (Landsat, DEPRECATED)",
            "wofs_summary_clear": "DEA Multi-Year Clear Observation Statistics (Landsat, DEPRECATED)",
            "wofs_summary_wet": "DEA Multi-Year Wet Observation Statistics (Landsat, DEPRECATED)",
            "Water Observations from Space Statistics": "DEA Multi-Year Water Observation Frequency Statistics (Landsat, DEPRECATED)",
            "wofs_filtered_summary_confidence": "DEA Multi-Year Water Observation Confidence Statistics (Landsat, DEPRECATED)",
            "ITEM_V2.0.0": "DEA Intertidal Extents (Landsat)",
            "ITEM_V2.0.0_Conf": "DEA Intertidal Extents confidence",
            "NIDEM": "DEA Intertidal Elevation (Landsat)",
            "high_tide_composite": "DEA High Tide Imagery (Landsat)",
            "low_tide_composite": "DEA Low Tide Imagery (Landsat)",
            "ga_s2_ba_provisional_3": "DEA Burnt Area Characteristic Layers (Sentinel 2 Near Real-Time, Provisional)",
            "alos_displacement": "ALOS Displacement",
            "alos_velocity": "ALOS Velocity",
            "envisat_displacement": "ENVISAT Displacement",
            "envisat_velocity": "ENVISAT Velocity",
            "radarsat2_displacement": "RADARSAT2 Displacement",
            "radarsat2_velocity": "RADARSAT2 Velocity",
            "aster_false_colour": "False Colour Mosaic",
            "aster_regolith_ratios": "Regolith Ratios",
            "aster_aloh_group_composition": "AlOH Group Composition",
            "aster_aloh_group_content": "AlOH Group Content",
            "aster_feoh_group_content": "FeOH Group Content",
            "aster_ferric_oxide_composition": "Ferric Oxide Composition",
            "aster_ferric_oxide_content": "Ferric Oxide Content",
            "aster_ferrous_iron_content_in_mgoh": "Ferrous Iron Content in MgOH/Carbonate",
            "aster_ferrous_iron_index": "Ferrous Iron Index",
            "aster_green_vegetation": "Green Vegetation Content",
            "aster_gypsum_index": "Gypsum Index",
            "aster_kaolin_group_index": "Kaolin Group Index",
            "aster_mgoh_group_composition": "MgOH Group Composition",
            "aster_mgoh_group_content": "MgOH Group Content",
            "aster_opaque_index": "Opaque Index",
            "aster_silica_index": "TIR Silica index",
            "aster_quartz_index": "TIR Quartz Index",
            "multi_scale_topographic_position": "Multi-Scale Topographic Position",
            "weathering_intensity": "Weathering Intensity",
        },
        "n_bands": {
            "ga_ls_ard_3": 7,
            "s2_nrt_granule_nbar_t": 23,
            "s2_ard_granule_nbar_t": 12,
            "ga_ls8c_nbart_gm_cyear_3": 10,
            "ga_ls7e_nbart_gm_cyear_3": 10,
            "ga_ls5t_nbart_gm_cyear_3": 10,
            "ga_ls8c_ard_3": 9,
            "ga_ls7e_ard_3": 8,
            "ga_ls5t_ard_3": 7,
            "ga_ls8c_ard_provisional_3": 9,
            "ga_ls7e_ard_provisional_3": 8,
            "ga_ls_ard_provisional_3": 7,
            "s2b_nrt_granule_nbar_t": 23,
            "s2a_nrt_granule_nbar_t": 23,
            "s2_nrt_provisional_granule_nbar_t": 12,
            "s2b_nrt_provisional_granule_nbar_t": 12,
            "s2a_nrt_provisional_granule_nbar_t": 12,
            "s2a_ard_granule_nbar_t": 12,
            "s2b_ard_granule_nbar_t": 12,
            "ga_ls_landcover": 2,
            "ga_ls_landcover_descriptors": 5,
            "ga_ls_fc_3": 4,
            "ga_ls_fc_pc_cyear_3": 10,
            "ga_ls_mangrove_cover_cyear_3": 1,
            "s2_barest_earth": 10,
            "ls8_barest_earth_mosaic": 6,
            "landsat_barest_earth": 6,
            "ga_ls_tcw_percentiles_2": 3,
            "ga_ls_tc_pc_cyear_3": 9,
            "ga_ls_wo_3": 1,
            "ga_ls_wo_fq_myear_3": 3,
            "ga_ls_wo_fq_cyear_3": 3,
            "ga_ls_wo_fq_apr_oct_3": 3,
            "ga_ls_wo_fq_nov_mar_3": 3,
            "wofs_filtered_summary": 2,
            "wofs_summary_clear": 3,
            "wofs_summary_wet": 3,
            "Water Observations from Space Statistics": 3,
            "wofs_filtered_summary_confidence": 2,
            "ITEM_V2.0.0": 1,
            "ITEM_V2.0.0_Conf": 1,
            "NIDEM": 1,
            "high_tide_composite": 6,
            "low_tide_composite": 6,
            "ga_s2_ba_provisional_3": None,
            "alos_displacement": 4,
            "alos_velocity": 4,
            "envisat_displacement": 4,
            "envisat_velocity": 4,
            "radarsat2_displacement": 4,
            "radarsat2_velocity": 4,
            "aster_false_colour": 3,
            "aster_regolith_ratios": 3,
            "aster_aloh_group_composition": 1,
            "aster_aloh_group_content": 1,
            "aster_feoh_group_content": 1,
            "aster_ferric_oxide_composition": 1,
            "aster_ferric_oxide_content": 1,
            "aster_ferrous_iron_content_in_mgoh": 1,
            "aster_ferrous_iron_index": 1,
            "aster_green_vegetation": 1,
            "aster_gypsum_index": 1,
            "aster_kaolin_group_index": 1,
            "aster_mgoh_group_composition": 1,
            "aster_mgoh_group_content": 1,
            "aster_opaque_index": 1,
            "aster_silica_index": 1,
            "aster_quartz_index": 1,
            "multi_scale_topographic_position": 3,
            "weathering_intensity": 1,
        },
        "date_limits": {
            "ga_ls_ard_3": ["1986-08-16", "2022-09-05"],
            "s2_nrt_granule_nbar_t": ["2022-06-20", "2022-09-19"],
            "s2_ard_granule_nbar_t": ["2015-07-12", "2022-09-13"],
            "ga_ls8c_nbart_gm_cyear_3": ["2013-01-01", "2021-01-01"],
            "ga_ls7e_nbart_gm_cyear_3": ["1999-01-01", "2021-01-01"],
            "ga_ls5t_nbart_gm_cyear_3": ["1986-01-01", "2011-01-01"],
            "ga_ls8c_ard_3": ["2013-03-19", "2022-09-05"],
            "ga_ls7e_ard_3": ["1999-05-28", "2022-04-06"],
            "ga_ls5t_ard_3": ["1986-08-16", "2011-11-17"],
            "ga_ls8c_ard_provisional_3": ["2022-06-20", "2022-09-19"],
            "ga_ls7e_ard_provisional_3": ["2022-06-22", "2022-08-24"],
            "ga_ls_ard_provisional_3": ["2022-06-20", "2022-09-19"],
            "s2b_nrt_granule_nbar_t": ["2022-06-20", "2022-09-19"],
            "s2a_nrt_granule_nbar_t": ["2022-06-20", "2022-09-19"],
            "s2_nrt_provisional_granule_nbar_t": ["2022-06-20", "2022-09-19"],
            "s2b_nrt_provisional_granule_nbar_t": ["2022-06-20", "2022-09-19"],
            "s2a_nrt_provisional_granule_nbar_t": ["2022-06-20", "2022-09-19"],
            "s2a_ard_granule_nbar_t": ["2015-07-12", "2022-09-13"],
            "s2b_ard_granule_nbar_t": ["2017-06-30", "2022-09-13"],
            "ga_ls_landcover": ["1988-01-01", "2020-01-01"],
            "ga_ls_landcover_descriptors": ["1988-01-01", "2020-01-01"],
            "ga_ls_fc_3": ["1986-08-16", "2022-09-05"],
            "ga_ls_fc_pc_cyear_3": ["1987-01-01", "2021-01-01"],
            "ga_ls_mangrove_cover_cyear_3": ["1987-01-01", "2021-01-01"],
            "s2_barest_earth": ["2017-01-01", "2017-01-01"],
            "ls8_barest_earth_mosaic": ["2013-01-01", "2013-01-01"],
            "landsat_barest_earth": ["1980-01-01", "1980-01-01"],
            "ga_ls_tcw_percentiles_2": ["1987-01-01", "1987-01-01"],
            "ga_ls_tc_pc_cyear_3": ["1987-01-01", "2021-01-01"],
            "ga_ls_wo_3": ["1986-08-16", "2022-09-05"],
            "ga_ls_wo_fq_myear_3": ["1986-01-01", "1986-01-01"],
            "ga_ls_wo_fq_cyear_3": ["1986-01-01", "2021-01-01"],
            "ga_ls_wo_fq_apr_oct_3": ["1986-04-01", "2021-04-01"],
            "ga_ls_wo_fq_nov_mar_3": ["1987-11-01", "2021-11-01"],
            "wofs_filtered_summary": ["1970-01-01", "1970-01-01"],
            "wofs_summary_clear": ["1970-01-01", "1970-01-01"],
            "wofs_summary_wet": ["1970-01-01", "1970-01-01"],
            "Water Observations from Space Statistics": ["1970-01-01", "1970-01-01"],
            "wofs_filtered_summary_confidence": ["1970-01-01", "1970-01-01"],
            "ITEM_V2.0.0": ["1986-01-01", "1986-01-01"],
            "ITEM_V2.0.0_Conf": ["1986-01-01", "1986-01-01"],
            "NIDEM": ["1986-01-01", "1986-01-01"],
            "high_tide_composite": ["2000-01-01", "2000-01-01"],
            "low_tide_composite": ["2000-01-01", "2000-01-01"],
            "ga_s2_ba_provisional_3": ["2021-10-01", "2022-09-19"],
            "alos_displacement": ["2008-02-11", "2010-10-22"],
            "alos_velocity": ["2009-06-15", "2009-06-15"],
            "envisat_displacement": ["2006-06-26", "2010-08-28"],
            "envisat_velocity": ["2008-06-15", "2008-06-15"],
            "radarsat2_displacement": ["2015-07-15", "2019-05-31"],
            "radarsat2_velocity": ["2017-06-15", "2017-06-15"],
            "aster_false_colour": ["2000-02-01", "2000-02-01"],
            "aster_regolith_ratios": ["2000-02-01", "2000-02-01"],
            "aster_aloh_group_composition": ["2000-02-01", "2000-02-01"],
            "aster_aloh_group_content": ["2000-02-01", "2000-02-01"],
            "aster_feoh_group_content": ["2000-02-01", "2000-02-01"],
            "aster_ferric_oxide_composition": ["2000-02-01", "2000-02-01"],
            "aster_ferric_oxide_content": ["2000-02-01", "2000-02-01"],
            "aster_ferrous_iron_content_in_mgoh": ["2000-02-01", "2000-02-01"],
            "aster_ferrous_iron_index": ["2000-02-01", "2000-02-01"],
            "aster_green_vegetation": ["2000-02-01", "2000-02-01"],
            "aster_gypsum_index": ["2000-02-01", "2000-02-01"],
            "aster_kaolin_group_index": ["2000-02-01", "2000-02-01"],
            "aster_mgoh_group_composition": ["2000-02-01", "2000-02-01"],
            "aster_mgoh_group_content": ["2000-02-01", "2000-02-01"],
            "aster_opaque_index": ["2000-02-01", "2000-02-01"],
            "aster_silica_index": ["2000-02-01", "2000-02-01"],
            "aster_quartz_index": ["2000-02-01", "2000-02-01"],
            "multi_scale_topographic_position": ["2018-01-01", "2018-01-01"],
            "weathering_intensity": ["2018-01-01", "2018-01-01"],
        },
    }
    return deadict


def getdict_license():
    """
    Retrieves the DEA data license and NCI attribution information as dict
    """
    dict = {
        "name": "Digital Earth Australia (DEA) Geoscience Earth Observations",
        "source_url": "https://docs.dea.ga.gov.au/notebooks/DEA_datasets/DEA_Landsat_Surface_Reflectance.html",
        "license": "CC BY 4.0",
        "license_title": "Creative Commons Attribution 4.0 International (CC BY 4.0)",
        "license_url": "https://creativecommons.org/licenses/by/4.0/",
        "copyright": "© Copyright 2017-2022, Geoscience Australia",
        "attribution": "Digital Earth Australia (DEA)",
    }
    return dict


def getdict_cloudmask():
    """
    return dict of cloud mask
    """
    oa_fmask = {
        "0": "nodata",
        "1": "valid",
        "2": "cloud",
        "3": "shadow",
        "4": "snow",
        "5": "water",
    }
    return oa_fmask


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
    wcs = WebCoverageService(url, timeout=300)

    # Get coverages and content dict keys
    content = wcs.contents
    keys = content.keys()

    print("Following data layers are available:")
    title_list = []
    description_list = []
    bbox_list = []
    timelimits = []
    for key in keys:
        print(f"key: {key}")
        print(f"title: {wcs[key].title}")
        title_list.append(wcs[key].title)
        print(f"{wcs[key].abstract}")
        description_list.append(wcs[key].abstract)
        print(f"bounding box: {wcs[key].boundingBoxWGS84}")
        bbox_list.append(wcs[key].boundingBoxWGS84)
        print(f"timelimits: {wcs[key].timelimits}")
        timelimits.append(wcs[key].timelimits)
        print("")
    nbands = []
    # Get number of bands (need to retrieve small subset)
    bbox = [130, -30.2, 130.2, -30]
    print("Requesting number of bands for each key...")
    for key in keys:
        try:
            response = wcs.getCoverage(
                identifier=key,
                bbox=bbox,
                format="GeoTIFF",
                crs="EPSG:4326",
                width=4,
                height=4,
                Styles="tc",
            )
            with MemoryFile(response) as memfile:
                with memfile.open() as dataset:
                    nband = dataset.count
            print(f"{key} has {nband} bands.")
        except:
            print(f"{key} failed to download")
            nband = None
        nbands.append(nband)
    return keys, title_list, description_list, bbox_list, timelimits, nbands


def write_deadict():
    """
    Generates new DEA dictionary from crawling WCS url
    """
    url = "https://ows.dea.ga.gov.au/?version=1.3.0"
    (
        keys,
        title_list,
        description_list,
        bbox_list,
        timelimits,
        nbands,
    ) = get_capabilities(url)

    deadict = {"resolution_arcsec": 1}
    layernames = {}
    n_bands = {}
    date_limits = {}
    deadict["resolution_arcsec"] = 1
    for i in range(len(keys)):
        layernames[keys[i]] = title_list[i]
        n_bands[keys[i]] = nbands[i]
        date_limits[keys[i]] = timelimits[i]

    deadict["layernames"] = layernames
    deadict["n_bands"] = n_bands
    deadict["date_limits"] = date_limits
    return deadict


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


def get_times_startend(url, layername, dt_start, dt_end):
    """
    Return all available images datetimes for layer in range
    between start and end date.

    Parameters
    ----------
    url: str, layer url
    layername: str, name of layer id
    dt_start: str, start date in dateformat YYYY-MM-DD
    dt_end: str, end date in dateformat YYYY-MM-DD

    Return
    ------
    list of dates
    """
    # Convert to datetimes
    dt_start = datetime.strptime(dt_start, "%Y-%m-%d")
    dt_end = datetime.strptime(dt_end, "%Y-%m-%d")
    wcs = WebCoverageService(url, version="1.0.0", timeout=300)
    times = wcs[layername].timepositions
    dates = []
    for time in times:
        dt = datetime.fromisoformat(time[:-1])
        if (dt >= dt_start) & (dt <= dt_end):
            dates.append(time)
    return dates


def get_wcsmap(
    outfname,
    layername,
    bbox,
    date,
    resolution,
    url,
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
        print(
            colored("\u2691", "yellow"),
            f"{layername}.tif already exists, skipping download",
        )
        # logging.warning(f"▲ | Download skipped: {layername} already exists")
        # logging.info(f"  | Location: {outfname}")
    else:
        try:
            with spin(f"Downloading {layername}.tif for date: {date}") as s:
                wcs = WebCoverageService(url, version="1.0.0", timeout=300)
                if date == "None":
                    data = wcs.getCoverage(
                        identifier=layername,
                        bbox=bbox,
                        format=format_out,
                        crs=crs,
                        width=nwidth,
                        height=nheight,
                        Styles="tc",
                    )
                else:
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
                s(1)
        except:
            print("Download failed")
            return False
        # Save data
        with open(outfname, "wb") as f:
            f.write(data.read())
    return True


def get_dea_layers(
    layernames,
    years,
    bbox,
    resolution,
    outpath,
    crs="EPSG:4326",
    format_out="GeoTIFF",
    verbose=False,
):
    """
    Get all images for all layers and all dates between start_date and end_date.
    Downloaded images are saved in outpath.

    Parameters
    ----------
    layernames : list of strings
        layer identifiers
    years : list
        years, e.g. [2019, 2020]
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
    list of output filenames for each layer
    """
    # Logger setup
    if verbose:
        write_logs.setup(level="info")
    else:
        write_logs.setup()

    # Check if input is list
    if not (isinstance(years, tuple) | isinstance(years, list)):
        years = [years]
    if not (isinstance(layernames, tuple) | isinstance(layernames, list)):
        layernames = [layernames]
    # Loop over layernames
    # logging.print("Processing DEA...")
    fnames_out = []
    for layername in layernames:
        # save for each layer
        outfnames = []
        for year in years:
            outfnames += get_dea_images(
                layername,
                year,
                bbox,
                resolution,
                outpath,
                crs=crs,
                format_out=format_out,
            )
        fnames_out += outfnames
    # logging.print(f"DEA download(s) complete (saved to: {outpath})")
    return fnames_out


def get_dea_images(
    layername,
    year,
    bbox,
    resolution,
    outpath,
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
        selected year for images
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

    # URL
    url = "https://ows.dea.ga.gov.au/?version=1.3.0"

    # Check if layername is defined
    dict_dea = get_deadict()
    if layername not in dict_dea["layernames"]:
        print(f"△ | {layername} not a DEA layer. Please select one of the following:")
        for key in dict_dea:
            print(key)

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
        # logging.print(f"Number of images for {year} found: {len(dates)}")
        # if len(dates) == 0:
        #     logging.warning(
        #         f"No dates found for year {year}. Trying to download without date..."
        #     )
    if len(dates) == 0:
        dates = ["None"]
    # Download images for all dates in year
    outfnames = []
    for date in dates:
        if format_out == "GeoTIFF":
            fname_end = ".tif"
        elif format_out == "NetCDF":
            fname_end = ".nc"
        else:
            logging.print(
                f"△ | {format_out} not supported. Choose either GeoTIFF or NetCDF."
            )
        if date == "None":
            fname_out = f"{layername}{fname_end}"
            outfname = os.path.join(outpath, fname_out)
        else:
            datestring = datetime.fromisoformat(date[:-1]).astimezone(timezone.utc)
            fname_out = f"{layername}_{datestring.year}-{datestring.month}-{datestring.day}{fname_end}"
        outfname = os.path.join(outpath, fname_out)
        # Get data
        download_ok = get_wcsmap(
            outfname,
            layername,
            bbox,
            date,
            resolution,
            url,
            crs=crs,
            format_out=format_out,
        )
        # Log download success message if file does not already exist
        if download_ok:
            outfnames.append(outfname)
        else:
            cprint(f"✘ {layername} for date {date} failed to download", "red")
    return outfnames


### Some test functions ###


def test_get_capabilities():
    """
    Test script to retrieve WCS capabilities
    """
    # DEA layer
    url = "https://ows.dea.ga.gov.au/?version=1.3.0"
    # Get capabilities
    keys, titles, descriptions, bboxs = get_capabilities(url)
    assert len(keys) > 0


def test_get_times():
    """
    Test script to retrieve available times for a layer
    """
    layername = "ga_ls8c_ard_3"
    url = "https://ows.dea.ga.gov.au/?version=1.3.0"
    times = get_times(url, layername)
    assert len(times) > 0


def test_get_times_startend():
    """
    Test script to retrieve available times for a layer
    """
    layername = "ga_ls8c_ard_3"
    url = "https://ows.dea.ga.gov.au/?version=1.3.0"
    dt_start = "2020-01-01"
    dt_end = "2020-02-20"
    times = get_times_startend(url, layername, dt_start, dt_end)
    assert len(times) > 0


def test_get_wcsmap():
    """
    Test script to retrieve and save image for one layer and date
    """
    url = "https://ows.dea.ga.gov.au/?version=1.3.0"
    layername = "ga_ls8c_ard_3"
    times = get_times(url, layername)
    crs = "EPSG:4326"  # WGS84
    # define bounding box for retrieval (simple test here for entire Australia)
    bbox = [130, -40, 150, -20]
    # define resolution (in arcsecs per pixel since crs is in WGS84)
    resolution = 100
    # get latest image
    time = times[-1]
    # define output file name
    fname_out = f"test_{layername}_{time}.tif"
    # Get data
    download_ok = get_wcsmap(fname_out, layername, bbox, time, resolution, url)
    assert download_ok


def test_get_dea_images():
    """
    Test script to retrieve and save images for a given year
    """
    url = "https://ows.dea.ga.gov.au/?version=1.3.0"
    # Get data (here only for first layer)
    layername = "ga_ls8c_ard_3"
    # Crs for output
    crs = "EPSG:4326"  # WGS84
    # define bounding box for retrieval (simple test here for entire Australia)
    bbox = [120, -40, 140, -20]
    # define resolution (in arcsecs per pixel since crs is in WGS84)
    resolution = 100
    # define year
    year = 2019
    # define outpath
    outpath = "test_dea"
    # Get data
    outfnames = get_dea_images(layername, year, bbox, resolution, outpath, crs=crs)
    assert len(outfnames) > 0
