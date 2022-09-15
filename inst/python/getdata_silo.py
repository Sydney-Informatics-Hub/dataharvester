"""
Python script to automatically download and crop climate data layers from SILO.

Functionalities:
- download SILO data for custom time period and layer(s) as defined in dictionary
- clip data to custom bounding box
- save data as multi-band geotiff or netCDF

The SILO climate layers are described as dictionary in the module function get_silodict()
and the SILO licensing and attribution are availabe with the module function getdict_license()

More details on the SILO climate variables can be found here:
https://www.longpaddock.qld.gov.au/silo/about/climate-variables/
and more details about the gridded data structure here:
https://www.longpaddock.qld.gov.au/silo/gridded-data/
and a data index:
https://s3-ap-southeast-2.amazonaws.com/silo-open-data/Official/annual/index.html

This package is part of the Data Harvester project developed for the Agricultural Research Federation (AgReFed).

Copyright 2022 Sydney Informatics Hub (SIH), The University of Sydney

This open-source software is released under the LGPL-3.0 License.

Author: Sebastian Haan
"""

import os
import shutil
import datetime
import requests

# from urllib import request
from pathlib import Path

# from netCDF4 import Dataset
# import rasterio
# import rioxarray as rio
import xarray

# logger setup
import write_logs
import logging

# from datacube.utils.cog import write_cog
from termcolor import cprint, colored
from alive_progress import alive_bar, config_handler

config_handler.set_global(
    force_tty=True,
    bar=None,
    spinner="waves",
    monitor=False,
    stats=False,
    receipt=True,
    elapsed="{elapsed}",
)
def spin(message=None, colour=None):
    """Spin animation as a progress inidicator"""
    return alive_bar(1, title=colored(f"{message} ", colour))


def download_file(url, year, outpath="."):
    """
    download file from url

    INPUT:
    url : str
    outpath : str

    OUTPUT:
    file : str
    """
    local_filename = os.path.join(outpath, url.split("/")[-1])
    filename_only = Path(outpath).name
    if os.path.exists(local_filename):
        cprint(f"⚑ {filename_only} already exists, skipping download", "yellow")
        # logging.info(f"  | Location: {local_filename}")
        return local_filename
    with spin(f"⇩ {filename_only} for year: {str(year)}", "blue") as s:
        with requests.get(url, stream=True) as r:
            with open(local_filename, "wb") as f:
                shutil.copyfileobj(r.raw, f)
        s(1)

    # with request.urlopen(url) as response:
    #     with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
    #         shutil.copyfileobj(response, tmp_file)
    # return tmp_file.name
    return local_filename


def get_silodict():
    """
    Get dictionary of available layers and meta data

    OUTPUT:
    layerdict : dict
        dictionary of meta data and available layer names
    """

    silodict = {}
    silodict["title"] = "SILO climate database"
    silodict[
        "description"
    ] = "SILO is containing continuous daily climate data for Australia from 1889 to present."
    silodict["crs"] = "EPSG:4326"
    silodict["bbox"] = [112.00, -44.00, 154.00, -10.00]
    silodict["resolution_arcsec"] = 180
    silodict["updates"] = "daily"
    silodict["layernames"] = {
        "daily_rain": "Daily rainfall, mm",
        "monthly_rain": "Monthly rainfall, mm",
        "max_temp": "Maximum temperature, degrees Celsius",
        "min_temp": "Minimum temperature, degrees Celsius",
        "vp": "Vapour pressure, hPa",
        "vp_deficit": "Vapour pressure deficit, hPa",
        "evap_pan": "Class A pan evaporation, mm",
        "evap_syn": "Synthetic estimate, mm",
        "evap_comb": "Combination: synthetic estimate pre-1970, class A pan 1970 onwards, mm",
        "evap_morton_lake": "Morton's shallow lake evaporation, mm",
        "radiation": "Solar radiation: Solar exposure, consisting of both direct and diffuse components, MJ/m2",
        "rh_tmax": "Relative humidity:	Relative humidity at the time of maximum temperature, %",
        "rh_tmin": "Relative humidity at the time of minimum temperature, %",
        "et_short_crop": "Evapotranspiration FAO564 short crop, mm",
        "et_tall_crop": "ASCE5 tall crop6, mm",
        "et_morton_actual": "Morton's areal actual evapotranspiration, mm",
        "et_morton_potential": "Morton's point potential evapotranspiration, mm",
        "et_morton_wet": "Morton's wet-environment areal potential evapotranspiration over land, mm",
        "mslp": "Mean sea level pressure Mean sea level pressure, hPa",
    }
    return silodict


def getdict_license():
    """
    Retrieves the SILO license and attribution information as dict
    """
    dict = {
        "name": "SILO Climate Data",
        "source_url": "https://www.longpaddock.qld.gov.au/silo/",
        "license": "CC BY 4.0",
        "license_title": "Creative Commons Attribution 4.0 International (CC BY 4.0)",
        "license_url": "https://creativecommons.org/licenses/by/4.0/",
        "copyright": "© State of Queensland (Queensland Department of Environment and Science) 2020.",
        "attribution": "State of Queensland (Queensland Department of Environment and Science) 2020.",
    }
    return dict


def xarray2tif(ds, outpath, outfname, layername):
    """
    Convert rio xarray dataset to multi-band geotiff with each time as separate band.

    TBD: optional: save separate tif each time slice

    INPUT:
    ds : xarray dataset
    outpath : str
        path to output directory
    outfname : str
        name of output file (".tif")

    OUTPUT:
    tif : str, name of multi-band geotiff
    """

    os.makedirs(name=outpath, exist_ok=True)

    # create empty array
    dsnew = xarray.Dataset()

    for i in range(len(ds.time)):

        # We will use the date of the image to name the GeoTIFF
        date = ds.isel(time=i).time.dt.strftime("%Y-%m-%d").data
        # print(f'Writing {date}')

        da = ds.isel(time=i)
        dsnew[str(date)] = xarray.DataArray(
            da.variables[layername][:],
            dims=["lat", "lon"],
            coords={"lat": da.variables["lat"], "lon": da.variables["lon"]},
        )

        # Write GeoTIFF with datacube libary for cloud optimized GeoTIFFs (COG)
        # write_cog(geo_im=singletimestamp_da,
        #         fname=os.path.join(outpath,f'{outfname_base}_{date}.tif',
        #         overwrite=True)
    # Set crs
    dsnew.rio.write_crs(4326, inplace=True)

    # Write GeoTIFF to disk
    dsnew.rio.to_raster(os.path.join(outpath, outfname))


def get_SILO_raster(
    layername,
    years,
    outpath,
    bbox=None,
    format_out="nc",
    delete_temp=False,
    verbose=False,
):
    """
    Get raster data from SILO for certain climate variable and save data as geotif.
    If multiple times are requested, then each time will be saved in on band of multi-band geotif.
    All layers are available with daily resolution (except 'monthly_rain')

    This function includes validation of years and automatically download of data from SILO in temporary folder.

    Input:
        layername : str, climate variable name (see below)
        years : list of years
        outpath : str, path to save output data
        bbox : list of bounding box coordinates (optional)
        format_out : str, format of output data: either 'nc' (netCDF) or 'tif' (geotiff)
        delete_temp : bool, delete temporary folder after download

    Returns:
        fnames_out : list of output filenames



    layer names:
        - 'daily_rain' (Daily rainfall, mm)
        - 'monthly_rain' (Monthly rainfall, mm)
        - 'max_temp' (Maximum temperature, deg C)
        - 'min_temp'  (Minimum temperature. deg C)
        - 'vp' (Vapour pressure, hPa)
        - 'vp_deficit' (Vapour pressure deficit, hPa)
        - 'evap_pan' (Class A pan evaporation, mm)
        - 'evap_syn' (Synthetic estimate, mm)
        - 'evap_comb' (Combination: synthetic estimate pre-1970, class A pan 1970 onwards, mm)
        - 'evap_morton_lake' (Morton's shallow lake evaporation, mm)
        - 'radiation'	(Solar radiation: Solar exposure, consisting of both direct and diffuse components, MJ/m2)
        - 'rh_tmax'	(Relative humidity:	Relative humidity at the time of maximum temperature, %)
        - 'rh_tmin'	(Relative humidity at the time of minimum temperature, %)
        - 'et_short_crop' (Evapotranspiration FAO564 short crop, mm)
        - 'et_tall_crop' (ASCE5 tall crop6, mm)
        - 'et_morton_actual' (Morton's areal actual evapotranspiration, mm)
        - 'et_morton_potential'	(Morton's point potential evapotranspiration, mm)
        - 'et_morton_wet' (Morton's wet-environment areal potential evapotranspiration over land, mm)
        - 'mslp' (Mean sea level pressure Mean sea level pressure, hPa)

    For more details see:
    SILO data structure doc for gridded data:
    https://www.longpaddock.qld.gov.au/silo/gridded-data/

    SILO url structure:
    url = "https://s3-ap-southeast-2.amazonaws.com/silo-open-data/Official/annual/<variable>/<year>.<variable>.nc
    e.g. url = "https://s3-ap-southeast-2.amazonaws.com/silo-open-data/Official/annual/monthly_rain/2005.monthly_rain.nc"
    """

    # Logger setup
    if verbose:
        write_logs.setup(level="info")
    else:
        write_logs.setup()

    # Check if layername is valid
    silodict = get_silodict()
    layerdict = silodict["layernames"]
    if layername not in layerdict:
        raise ValueError("Layer name not valid. Choose from: " + str(layerdict.keys()))

    # Create output folder
    os.makedirs(outpath, exist_ok=True)

    # Check if years are valid
    if not (isinstance(years, tuple) | isinstance(years, list)):
        # If not a list, make it a list
        years = [years]
    # Get current year from datetime
    current_year = int(datetime.datetime.now().year)

    # Check if format is valid
    if format_out not in ["nc", "tif"]:
        logging.error("Output format not valid. Choose from: 'nc' or 'tif'")
        raise ValueError("Output format not valid. Choose from: 'nc' or 'tif'")

    # Check if years are in the range of available years
    url_info = "https://www.longpaddock.qld.gov.au/silo/gridded-data/"
    for year in years:
        if year > current_year:
            logging.error(f"! | Choose years <= {current_year}")
            raise ValueError(f"Choose years <= {current_year}")
            return False
        if year < 1889:
            logging.error(
                "! | data is not available for years < 1889. ",
                f"see for more details: {url_info}",
            )
            return False
        if (year < 1970) & (layername == "evap_pan"):
            logging.error(
                f"! | {layername} is not available for years < 1970. Automatically set to evap_comb"
            )
            logging.error(f"see for more details: {url_info}")
            layername = "evap_comb"
        if (year < 1957) & (layername == "mslp"):
            logging.error(
                f"! | {layername} is not available for years < 1957.",
                f"see for more details: {url_info}",
            )
            return False

    # Silo base url
    silo_baseurl = (
        "https://s3-ap-southeast-2.amazonaws.com/silo-open-data/Official/annual/"
    )
    # print(f"Processing {layername} (SILO)...")
    fnames_out = []
    # Download data for each year and save as geotif
    for year in years:
        # Get url
        url = silo_baseurl + layername + "/" + str(year) + "." + layername + ".nc"
        # Download file
        # logging.info(f"Downloading data from {url} ...")
        if os.path.exists(os.path.join(outpath, url.split("/")[-1])):
            file_exists = True
        else:
            file_exists = False
        filename = download_file(url, year, outpath)
        # Open file in Xarray
        ds = xarray.open_dataset(filename)
        # select data in bbox:
        if bbox is not None:
            ds = ds.sel(lon=slice(bbox[0], bbox[2]), lat=slice(bbox[1], bbox[3]))
        # Save data
        if format_out == "nc":
            # Save netCDF file
            outfname = layername + "_" + str(year) + "_cropped.nc"
            outfile = os.path.join(outpath, outfname)
            ds.to_netcdf(outfile)
        elif format_out == "tif":
            # Save as multi-band geotiff file
            outfname = layername + "_" + str(year) + "_cropped.tif"
            xarray2tif(ds, outpath, outfname, layername)
        # Close file
        ds.close()
        # Remove file
        if delete_temp:
            os.remove(filename)
        # if not file_exists:
        #     print(f"⇩ {layername} for year: {str(year)}")
        # logging.info(f"  | Saved as geotif: {os.path.join(outpath, outfname)}")
        fnames_out.append(os.path.join(outpath, outfname))
    # logging.print(f"SILO download(s) complete: {layername}")
    # Convert netcdf to geotif
    # nc_to_geotif(filename, outpath, layername, year)
    # https://pratiman-91.github.io/2020/08/01/NetCDF-to-GeoTIFF-using-Python.html
    return fnames_out


### Test function ###


def test_get_SILO_raster():
    """
    test script
    """
    layername = "daily_rain"
    years = 2019
    outpath = "silo_test"
    bbox = (130, -44, 153.9, -11)
    # test first for tif output format
    format_out = "tif"
    fnames_out = get_SILO_raster(layername, years, outpath, bbox, format_out)
    assert len(fnames_out) > 0
