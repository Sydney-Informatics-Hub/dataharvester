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
            "ga_ls_ard_3": "DEA Surface Reflectance (Landsat)",
            "s2_nrt_granule_nbar_t": "DEA Surface Reflectance (Sentinel-2 Near Real-Time)",
            "s2_ard_granule_nbar_t": "DEA Surface Reflectance (Sentinel-2)",
            "ls8_nbart_geomedian_annual": "DEA Surface Reflectance Calendar Year (Landsat 8 OLI-TIRS)",
            "ls7_nbart_geomedian_annual": "DEA Surface Reflectance Calendar Year (Landsat 7 ETM+)",
            "ls5_nbart_geomedian_annual": "DEA Surface Reflectance Calendar Year (Landsat 5 TM)",
            "ls8_nbart_tmad_annual": "DEA Surface Reflectance TMAD Calendar Year (Landsat 8 OLI-TIRS)",
            "ls7_nbart_tmad_annual": "DEA Surface Reflectance TMAD Calendar Year (Landsat 7 ETM+)",
            "ls5_nbart_tmad_annual": "DEA Surface Reflectance TMAD Calendar Year (Landsat 5 TM)",
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
            "fcp_rgb": "DEA Fractional Cover Percentiles (Landsat, Annual)",
            "fcp_seasonal_rgb": "DEA Fractional Cover Percentiles (Landsat, Seasonal)",
            "fcp_green_veg": "DEA Fractional Cover Percentiles (Landsat, Annual, Green Vegetation)",
            "fcp_non_green_veg": "DEA Fractional Cover Percentiles (Landsat, Annual, Non-Green Vegetation)",
            "fcp_bare_ground": "DEA Fractional Cover Percentiles (Landsat, Annual, Bare Ground)",
            "fcp_seasonal_green_veg": "DEA Fractional Cover Percentiles (Landsat, Seasonal, Green Vegetation)",
            "fcp_seasonal_non_green_veg": "DEA Fractional Cover Percentiles (Landsat, Seasonal, Non-Green Vegetation)",
            "fcp_seasonal_bare_ground": "DEA Fractional Cover Percentiles (Landsat, Seasonal, Bare Ground)",
            "ls5_fc_albers": "DEA Fractional Cover (Landsat 5 TM, Collection 2)",
            "ls7_fc_albers": "DEA Fractional Cover (Landsat 7 ETM+, Collection 2)",
            "ls8_fc_albers": "DEA Fractional Cover (Landsat 8 OLI-TIRS, Collection 2)",
            "fc_albers_combined": "DEA Fractional Cover (Landsat, Collection 2)",
            "mangrove_cover_v2_0_2": "DEA Mangroves (Landsat)",
            "s2_barest_earth": "GA Barest Earth (Sentinel-2)",
            "ls8_barest_earth_mosaic": "GA Barest Earth (Landsat 8 OLI/TIRS)",
            "landsat_barest_earth": "GA Barest Earth (Landsat)",
            "ga_ls_tcw_percentiles_2": "DEA Wetness Percentiles (Landsat)",
            "ga_ls_wo_3": "DEA Water Observations (Landsat)",
            "ga_ls_wo_fq_myear_3": "Multi Year Water Observation Statistics (Landsat)",
            "ga_ls_wo_fq_cyear_3": "Annual Water Observation Statistics - Calendar Year (Landsat)",
            "ga_ls_wo_fq_apr_oct_3": "Seasonal Water Observation Statistics - April to October (Landsat)",
            "ga_ls_wo_fq_nov_mar_3": "Seasonal Water Observation Statistics - November to March (Landsat)",
            "wofs_albers": "DEA Water Observations (Landsat, depricated)",
            "wofs_annual_summary_statistics": "DEA Annual Water Observation Frequency Statistics (Landsat, depricated)",
            "wofs_annual_summary_clear": "DEA Annual Clear Observation Statistics (Landsat, C2)",
            "wofs_annual_summary_wet": "DEA Annual Wet Observation Statistics (Landsat, depricated)",
            "wofs_filtered_summary": "DEA Multi-Year Water Observation Frequency Filtered Statistics (Landsat, depricated)",
            "wofs_summary_clear": "DEA Multi-Year Clear Observation Statistics (Landsat, depricated)",
            "wofs_summary_wet": "DEA Multi-Year Wet Observation Statistics (Landsat, depricated)",
            "Water Observations from Space Statistics": "DEA Multi-Year Water Observation Frequency Statistics (Landsat, depricated)",
            "wofs_filtered_summary_confidence": "DEA Multi-Year Water Observation Confidence Statistics (Landsat, depricated)",
            "wofs_apr_oct_summary_statistics": "DEA April-October Seasonal Water Observations (Landsat, depricated)",
            "wofs_apr_oct_summary_clear": "DEA April-October Clear Observation Statistics (Landsat, depricated)",
            "wofs_apr_oct_summary_wet": "DEA April-October Wet Observation Statistics (Landsat, depricated)",
            "wofs_nov_mar_summary_statistics": "DEA November-March Seasonal Water Observations (Landsat, depricated)",
            "wofs_nov_mar_summary_clear": "DEA November-March Clear Observation Statistics (Landsat, depricated)",
            "wofs_nov_mar_summary_wet": "DEA November-March Wet Observation Statistics (Landsat, depricated)",
            "ITEM_V2.0.0": "DEA Intertidal Extents (ITEM)",
            "ITEM_V2.0.0_Conf": "DEA Intertidal Extents confidence",
            "NIDEM": "DEA Intertidal Elevation (NIDEM)",
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
        logging.warning(f"▲ | Download skipped: {layername} already exists")
        logging.info(f"  | Location: {outfname}")
    else:
        try:
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
    logging.print("Processing DEA...")
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
        fnames_out.append(outfnames)
    logging.print(f"DEA download(s) complete (saved to: {outpath})")
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
    logging.print(f"Number of images for {year} found: {len(dates)}")
    if len(dates) == 0:
        logging.warning(
            f"No dates found for year {year}. Trying to download without date..."
        )
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
        if os.path.exists(outfname):
            exists = True
            outfnames.append(outfname)
        else:
            exists = False
        # Get data
        logging.info(f"Downloading {layername} for date {date}...")
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
            if not exists:
                if len(date) == 0:
                    logging.print(f"✔ | {layername}")
                else:
                    logging.print(f"✔ | {layername} for date: {date}")
            outfnames.append(outfname)
        else:
            if len(dates) == 0:
                logging.print(f"✘ | {layername} failed to download")
            else:
                logging.print(f"✘ | {layername} for date {date} failed to download")
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
