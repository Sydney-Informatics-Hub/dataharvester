"""
This script is used to run the headless version of the data harvester.
"""

# TODO: add validation to infile, colname_lng, colname_lat, if not in config, to
# generate blanks so that the script doesn't crash. In the future, maybe let the
# main code handle this, but for now, this is a quick fix.

import os

from pathlib import Path

import geopandas as gpd
import getdata_dea
import getdata_dem
import getdata_ee
import getdata_landscape
import getdata_radiometric
import getdata_silo
import getdata_slga
import utils
from termcolor import cprint
from types import SimpleNamespace
from utils import init_logtable, update_logtable
import yaml


def run(path_to_config, log_name="download_log", preview=False, return_df=False):
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

    # Load config file (based on notebook for now, will optimise later)
    with open(path_to_config, "r") as f:
        settings = yaml.load(f, Loader=yaml.SafeLoader)

    # Count number of sources to download from
    count_sources = len(settings["target_sources"])
    list_sources = list(settings["target_sources"].keys())

    # If no infile provided, generate a blank one (including colnames)
    try:
        settings["infile"]
        points_available = True
    except (AttributeError, KeyError):
        settings["infile"] = None
        settings["colname_lng"] = None
        settings["colname_lat"] = None
        points_available = False

    # If no resolution set, make it 1 arc-second
    if settings["target_res"] is None:
        cprint("ⓘ No target resolution specified, using default of 1 arc-sec", "yellow")
        settings["target_res"] = 1

    # Create bounding box if infile is provided and target_bbox is not provided
    if settings["infile"] is not None and settings["target_bbox"] is None:
        gdfpoints = gpd.read_file(settings["infile"])
        longs = gdfpoints[settings["colname_lng"]].astype(float)
        lats = gdfpoints[settings["colname_lat"]].astype(float)
        settings["target_bbox"] = (
            min(longs) - 0.05,
            min(lats) - 0.05,
            max(longs) + 0.05,
            max(lats) + 0.05,
        )

    # Stop if bounding box cannot be calculated or was not provided
    if settings["infile"] is None and settings["target_bbox"] is None:
        raise ValueError("No sampling file or bounding box provided")

    # Create download log
    download_log = init_logtable()
    # process each data source
    cprint(f"ⓘ Found the following {count_sources} sources: {list_sources}", "blue")
    cprint("\nDownloading data -----", "magenta", attrs=["bold"])

    # GEE
    if "GEE" in list_sources:
        # Try to initialise API if Earth Engine is selected
        getdata_ee.initialise()

        cprint("\n⌛ Downloading Google Earth Engine data...", attrs=["bold"])
        # get data from GEE
        gee = getdata_ee.collect(config=path_to_config)
        gee = getdata_ee.harvest(gee, coords=settings["target_bbox"])
        outfnames = [settings["outpath"] + gee.filenames]
        layernames = [Path(gee.filenames).resolve().stem]

        download_log = update_logtable(
            download_log,
            outfnames,
            layernames,
            "GEE",
            SimpleNamespace(**settings),
            layertitles=[],
            agfunctions=gee.reduce,
            loginfos="downloaded",
        )
    # DEA
    if "DEA" in list_sources:
        cprint("\n⌛ Downloading DEA data...", attrs=["bold"])
        # get data from DEA
        dea_layernames = settings["target_sources"]["DEA"]
        outpath_dea = os.path.join(settings["outpath"], "dea")
        # put into subdirectory
        files_dea = getdata_dea.get_dea_layers(
            dea_layernames,
            settings["target_dates"],
            settings["target_bbox"],
            settings["target_res"],
            outpath_dea,
            crs="EPSG:4326",
            format_out="GeoTIFF",
        )
        download_log = update_logtable(
            download_log,
            files_dea,
            dea_layernames,
            "DEA",
            SimpleNamespace(**settings),
            layertitles=[],
            loginfos="downloaded",
        )
    # DEM
    if "DEM" in list_sources:
        cprint("\n⌛ Downloading DEM data...", attrs=["bold"])
        dem_layernames = settings["target_sources"]["DEM"]
        try:
            files_dem = getdata_dem.get_dem_layers(
                dem_layernames,
                settings["outpath"],
                settings["target_bbox"],
                settings["target_res"],
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
                SimpleNamespace(**settings),
                layertitles=dem_layernames,
                loginfos="downloaded",
            )
    if "Landscape" in list_sources:
        cprint("\n⌛ Downloading Landscape data...", attrs=["bold"])
        # get data from Landscape
        layernames = settings["target_sources"]["Landscape"]
        layertitles = ["landscape_" + layername for layername in layernames]

        files_ls = getdata_landscape.get_landscape_layers(
            layernames,
            settings["target_bbox"],
            settings["outpath"],
            resolution=settings["target_res"],
        )
        # Add extracted data to log dataframe
        download_log = update_logtable(
            download_log,
            files_ls,
            layernames,
            "Landscape",
            SimpleNamespace(**settings),
            layertitles=layertitles,
            loginfos="downloaded",
        )
    if "Radiometric" in list_sources:
        cprint("\n⌛ Downloading Radiometric data...", attrs=["bold"])
        # get data from Radiometric
        # Download radiometrics
        layernames = settings["target_sources"]["Radiometric"]
        try:
            files_rd = getdata_radiometric.get_radiometric_layers(
                settings["outpath"],
                layernames,
                bbox=settings["target_bbox"],
                resolution=settings["target_res"],
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
                SimpleNamespace(**settings),
                layertitles=layernames,
                loginfos="downloaded",
            )
        else:
            pass
    if "SILO" in list_sources:
        cprint("\n⌛ Downloading SILO data...", attrs=["bold"])
        # get data from SILO
        fnames_out_silo = []
        silo_layernames = list(settings["target_sources"]["SILO"].keys())
        try:
            for layername in silo_layernames:
                # run the download
                files_silo = settings["outpath"] + "silo_" + layername
                fnames_out = getdata_silo.get_SILO_raster(
                    layername,
                    settings["target_dates"],
                    files_silo,
                    bbox=settings["target_bbox"],
                    format_out="tif",
                    delete_temp=False,
                )
                # Save the layer name
                fnames_out_silo += fnames_out
        except Exception as e:
            print(e)
        var_exists = "files_silo" in locals() or "files_silo" in globals()
        if var_exists:
            # Add download info to log dataframe
            download_log = update_logtable(
                download_log,
                fnames_out_silo,
                silo_layernames,
                "SILO",
                SimpleNamespace(**settings),
                layertitles=[],
                loginfos="downloaded",
            )
        else:
            pass
    if "SLGA" in list_sources:
        cprint("\n⌛ Downloading SLGA data...", attrs=["bold"])
        # get data from SLGA
        depth_min, depth_max = getdata_slga.identifier2depthbounds(
            list(settings["target_sources"]["SLGA"].values())[0]
        )
        slga_layernames = list(settings["target_sources"]["SLGA"].keys())
        try:
            files_slga = getdata_slga.get_slga_layers(
                slga_layernames,
                settings["target_bbox"],
                settings["outpath"],
                depth_min=depth_min,
                depth_max=depth_max,
                get_ci=True,
            )
        except Exception as e:
            print(e)
        var_exists = "files_slga" in locals() or "files_slga" in globals()
        if var_exists:
            download_log = update_logtable(
                download_log,
                files_slga,
                slga_layernames,
                "SLGA",
                SimpleNamespace(**settings),
                layertitles=[],
                loginfos="downloaded",
            )
        else:
            pass

    # save log to file
    logfile = settings["outpath"] + log_name + ".csv"
    download_log.to_csv(logfile, index=False)

    # extract filename from settings["infile"]
    # Select all processed data
    df_sel = download_log.copy()
    rasters = df_sel["filename_out"].values.tolist()
    titles = df_sel["layertitle"].values.tolist()
    if points_available:
        fn = Path(settings["infile"]).resolve().name
        cprint(f"\nExtracting data points for {fn}  -----", "magenta", attrs=["bold"])
        # Extract datatable from rasters given input coordinates
        gdf = utils.raster_query(longs, lats, rasters, titles)
        # Save the results table to a csv
        gdf.to_csv(
            os.path.join(settings["outpath"], "results.csv"), index=True, mode="w"
        )
        # Save also as geopackage
        gdf.to_file(os.path.join(settings["outpath"], "results.gpkg"), driver="GPKG")
        cprint(
            f"✔ Data points extracted to {settings['outpath']}results.gpkg",
            "blue",
            attrs=["bold"],
        )

    if preview and points_available:
        utils.plot_rasters(rasters, longs, lats, titles)
    elif preview and not points_available:
        utils.plot_rasters(rasters, titles=titles)

    cprint("\n🎉 🎉 🎉 Harvest complete 🎉 🎉 🎉", "magenta", attrs=["bold"])

    if return_df and points_available:
        return gdf
    else:
        return None
