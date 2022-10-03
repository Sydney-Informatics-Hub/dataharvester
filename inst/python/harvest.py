"""
This script is used to run the headless version of the data harvester.
"""

import os

from os.path import exists
from pathlib import Path
import pandas as pd
from types import SimpleNamespace


import geopandas as gpd
import getdata_dea
import getdata_dem
import getdata_ee
import getdata_landscape
import getdata_radiometric
import getdata_silo
import getdata_slga
import utils
from arc2meter import calc_arc2meter
from termcolor import cprint
from utils import init_logtable, update_logtable
from widgets import harvesterwidgets as hw


def run(path_to_config, log_name="download_log", preview=False):
    """
    A headless version of the Data-Harvester (with some limitations)

    Parameters
    ----------
    path_to_config : str
        Path to YAML config file
    preview : bool, optional
        Plots a matrix of downloaded images if set to True, by default False

    Returns
    -------
    None
        Nothing is returned, results are saved to disk
    """
    cprint("Starting the data harvester -----\n", "magenta", attrs=["bold"])
    tab_nest, w_settings, names_settings, w_load = hw.gen_maintab()
    if path_to_config != "":
        # load settings fromm file given by command line argument
        cprint(f"ⓘ Parsing config from {path_to_config}", "blue")
        settings = hw.load_settings(path_to_config)
    elif w_load.value is None:
        # if no settings file selected, convert widgets inputs above to settings
        dict_settings = hw.eval_widgets(w_settings, names_settings)
        # Convert settings from dictionary to SimpleNamespace (so all settings names available as settings.xxxname)
        settings = SimpleNamespace(**dict_settings)
        # Check if output path exists, if not create it:
        os.makedirs(settings.outpath, exist_ok=True)
        # Save settings to yaml file:
        hw.save_dict_settings(
            dict_settings, os.path.join(settings.outpath, "settings_saved.yaml")
        )
    else:
        print(f"Settings loaded from {w_load.value}")
        settings = hw.load_settings(w_load.value)

    # parse what's available
    count_sources = len(settings.target_sources)
    list_sources = list(settings.target_sources.keys())

    # Quick checks
    if settings.infile is not None:
        points_available = True
    if settings.target_bbox is None or settings.target_bbox == "":
        aoi_available = None
    if settings.target_res is None:
        cprint("ⓘ No target resolution specified, using default of 1 arcsec", "yellow")
        settings.target_res = 1
    else:
        pass
    if "GEE" in list_sources:
        # cprint("ⓘ GEE source selected, checking credentials", "blue")
        getdata_ee.initialise()

    # extract data points if a point file is provided
    if points_available:
        gdfpoints = gpd.read_file(settings.infile)
        longs = gdfpoints[settings.colname_lng].astype(float)
        lats = gdfpoints[settings.colname_lat].astype(float)
    # if area of interest is not provided, generate bounding box from points
    if points_available and aoi_available is None:
        cprint(
            f"ⓘ No bounding box provided - will generate from points in {settings.infile}",
            "blue",
        )
        settings.target_bbox = (
            min(longs) - 0.05,
            min(lats) - 0.05,
            max(longs) + 0.05,
            max(lats) + 0.05,
        )
        # Estimate resolution in meters:
        lat_center = (settings.target_bbox[1] + settings.target_bbox[3]) / 2
        xres_meters, yres_meters = calc_arc2meter(settings.target_res, lat_center)
        cprint(f"✔ Bounding box generated: {settings.target_bbox}", "blue")
        # cprint(
        #     f"ⓘ {settings.target_res} arcsec resolution corresponds to "
        #     f"{xres_meters:.1f}m x {yres_meters:.1f}m in x,y direction "
        #     f"(at Latitude: {lat_center:.2f})",
        #     "blue",
        # )
    download_log = init_logtable()
    # process each data source
    cprint(f"ⓘ Found the following {count_sources} sources: {list_sources}", "blue")
    cprint("\nDownloading data -----", "magenta", attrs=["bold"])

    # GEE
    if "GEE" in list_sources:
        cprint("\n⌛ Downloading Google Earth Engine data...", attrs=["bold"])
        # get data from GEE
    gee = getdata_ee.collect(config=path_to_config)
    gee = getdata_ee.harvest(gee, coords=settings.target_bbox)
    outfnames = [settings.outpath + gee.filenames]
    layernames = [Path(gee.filenames).resolve().stem]
    # print(outfnames)
    # print(layernames)
    # print(gee.reduce)
    download_log = update_logtable(
        download_log,
        outfnames,
        layernames,
        "GEE",
        settings,
        layertitles=[],
        agfunctions=gee.reduce,
        loginfos="downloaded",
    )
    # DEA
    if "DEA" in list_sources:
        cprint("\n⌛ Downloading DEA data...", attrs=["bold"])
        # get data from DEA
        dea_layernames = settings.target_sources["DEA"]
        outpath_dea = os.path.join(settings.outpath, "dea")
        # put into subdirectory
        files_gee = getdata_dea.get_dea_layers(
            dea_layernames,
            settings.target_dates,
            settings.target_bbox,
            settings.target_res,
            outpath_dea,
            crs="EPSG:4326",
            format_out="GeoTIFF",
        )
        download_log = update_logtable(
            download_log,
            files_gee,
            dea_layernames,
            "DEA",
            settings,
            layertitles=[],
            loginfos="downloaded",
        )
    # DEM
    if "DEM" in list_sources:
        cprint("\n⌛ Downloading DEM data...", attrs=["bold"])
        dem_layernames = settings.target_sources["DEM"]
        try:
            files_dem = getdata_dem.get_dem_layers(
                dem_layernames,
                settings.outpath,
                settings.target_bbox,
                settings.target_res,
            )
        except Exception as e:
            print(e)
        # Check if output if False (no data available) and skip if so
        if (files_dem == [False]) or files_dem is None:
            pass
        else:
            # Add extracted data to log dataframe
            download_log = update_logtable(
                download_log,
                files_dem,
                dem_layernames,
                "DEM",
                settings,
                layertitles=dem_layernames,
                loginfos="downloaded",
            )
    if "Landscape" in list_sources:
        cprint("\n⌛ Downloading Landscape data...", attrs=["bold"])
        # get data from Landscape
        layernames = settings.target_sources["Landscape"]
        layertitles = ["landscape_" + layername for layername in layernames]

        files_ls = getdata_landscape.get_landscape_layers(
            layernames,
            settings.target_bbox,
            settings.outpath,
            resolution=settings.target_res,
        )
        # Add extracted data to log dataframe
        download_log = update_logtable(
            download_log,
            files_ls,
            layernames,
            "Landscape",
            settings,
            layertitles=layertitles,
            loginfos="downloaded",
        )
    if "Radiometric" in list_sources:
        cprint("\n⌛ Downloading Radiometric data...", attrs=["bold"])
        # get data from Radiometric
        # Download radiometrics
        layernames = settings.target_sources["Radiometric"]
        try:
            files_rd = getdata_radiometric.get_radiometric_layers(
                settings.outpath,
                layernames,
                bbox=settings.target_bbox,
                resolution=settings.target_res,
            )
        except Exception as e:
            print(e)
        var_exists = "files_rd" in locals() or "files_rd" in globals()
        if var_exists:
            # Add extracted data to log dataframe
            download_log = update_logtable(
                download_log,
                files_rd,
                layernames,
                "Radiometric",
                settings,
                layertitles=layernames,
                loginfos="downloaded",
            )
        else:
            pass
    if "SILO" in list_sources:
        cprint("\n⌛ Downloading SILO data...", attrs=["bold"])
        # get data from SILO
        fnames_out_silo = []
        silo_layernames = list(settings.target_sources["SILO"].keys())
        for layername in silo_layernames:
            # run the download
            files_silo = settings.outpath + "SILO_" + layername
            fnames_out = getdata_silo.get_SILO_raster(
                layername,
                settings.target_dates,
                files_silo,
                bbox=settings.target_bbox,
                format_out="tif",
                delete_temp=False,
            )
            # Save the layer name
            fnames_out_silo += fnames_out
        # Add download info to log dataframe
        download_log = update_logtable(
            download_log,
            fnames_out_silo,
            silo_layernames,
            "SILO",
            settings,
            layertitles=[],
            loginfos="downloaded",
        )
    if "SLGA" in list_sources:
        cprint("\n⌛ Downloading SLGA data...", attrs=["bold"])
        # get data from SLGA
        depth_min, depth_max = getdata_slga.identifier2depthbounds(
            list(settings.target_sources["SLGA"].values())[0]
        )
        slga_layernames = list(settings.target_sources["SLGA"].keys())
        files_slga = getdata_slga.get_slga_layers(
            slga_layernames,
            settings.target_bbox,
            settings.outpath,
            depth_min=depth_min,
            depth_max=depth_max,
            get_ci=True,
        )
        download_log = update_logtable(
            download_log,
            files_slga,
            slga_layernames,
            "SLGA",
            settings,
            layertitles=[],
            loginfos="downloaded",
        )

    # save log to file
    logfile = settings.outpath + log_name + ".csv"
    download_log.to_csv(logfile, index=False)

    if points_available:
        # extract filename from settings.infile
        fn = Path(settings.infile).resolve().name
        cprint(f"\nExtracting data points for {fn}  -----", "magenta", attrs=["bold"])
        # Select all processed data
        df_sel = download_log.copy()
        rasters = df_sel["filename_out"].values.tolist()
        titles = df_sel["layertitle"].values.tolist()
        # Extract datatable from rasters given input coordinates
        gdf = utils.raster_query(longs, lats, rasters, titles)
        # Save the results table to a csv
        gdf.to_csv(os.path.join(settings.outpath, "results.csv"), index=True, mode="w")
        # Save also as geopackage
        gdf.to_file(os.path.join(settings.outpath, "results.gpkg"), driver="GPKG")
        cprint(
            f"✔ Data points extracted to {settings.outpath}results.gpkg",
            "blue",
            attrs=["bold"],
        )
        cprint("\nSummary of data extracted -----", "magenta", attrs=["bold"])
        gdf.info()
    cprint("\n🎉 🎉 🎉 Harvest complete 🎉 🎉 🎉", "magenta", attrs=["bold"])

    if preview:
        cprint("\nPreview downloaded images", "magenta", attrs=["bold"])
        utils.plot_rasters(rasters, longs, lats, titles)
    return None
