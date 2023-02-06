#!/bin/python
"""
Initialise and download image data from Google Earth Engine. Restricted to
Sentinel and Landsat images only:

- Sentinel-1 SAR GRD: C-band Synthetic Aperture Radar
- Sentinel-2 MSI: Multispectral Instrument
- Landsat 4 TM Thematic Mapper 1982-1993
- Landsat 5 TM Thematic Mapper 1984-2012
- Landsat 7 ETM+ Enhanced Thematic Mapper Plus (ETM+) 1999-2021
- Landsat 8 OLI/TIRS Operational Land Imager (OLI) and Thermal Infrared Sensor
  (TIRS) 2013-Now 
- Landsat 9 OLI-2/TIRS-2 Operational Land Imager (OLI) and Thermal Infrared
  Sensor (TIRS) 2021-Now

For more information on these data sources, browse the Google Earth Engine Data
Catalog: https://developers.google.com/earth-engine/datasets.

MAX FILE DOWNLOAD SIZE LIMIT: 50331648 bytes (~ 50 MB)

Functions:
----------

preprocess(): filter, mask, buffer, reduce and/or clip an image collection
aggregate(): perform temporal aggregation on an image collection map(): preview
an image or image collection download(): download an image or image collection.


Copyright 2022 Sydney Informatics Hub (SIH), The University of Sydney. This open
source software is released under the LGPL-3.0 License.

"""
import datetime
import ee
import eemont  # trunk-ignore(flake8/F401)
import geemap.foliumap as geemap
import geemap.colormaps as cm
import math
import os
import rioxarray
import wxee  # trunk-ignore(flake8/F401)
import yaml
import urllib
import json
import utils
import settingshandler as sh

from utils import spin
from contextlib import contextmanager, redirect_stderr, redirect_stdout
from functools import partialmethod

from os import devnull

# from termcolor import colored
from termcolor import cprint
from tqdm.notebook import tqdm


@contextmanager
def suppress():
    """
    A context manager that redirects stdout and stderr to devnull

    From https://stackoverflow.com/a/52442331.
    """
    with open(devnull, "w") as fnull:
        with redirect_stderr(fnull) as err, redirect_stdout(fnull) as out:
            yield (err, out)


def initialise(auth_mode="gcloud"):
    """
    Initialise Google Earth Engine API

    Try to initialise Google Earth Engine API. If it fails, the user is prompted
    to authenticate through the command line interface.
    """
    # Check if initialised:
    if ee.data._credentials:
        utils.msg_warn("Earth Engine API already authenticated")
    else:
        with spin("Initialising Earth Engine...") as s:
            geemap.ee_initialize(auth_mode=auth_mode)
            s(1)
        if ee.data._credentials:
            utils.msg_success("Earth Engine authenticated")
        else:
            utils.msg_warn("Please run this function again to authenticate")


class collect:
    """
    A class to manipulate Google Earth Engine objects

    This class brings additional packages into the mix to manipulate Earth
    Engine objects, specifically images.

    Attributes
    ----------
    config: str
        Path string to a YAML configuration file. A default configuration file
        can be generated for editing using `template()` method.
    collection: str
        A Google Earth Engine collection. Collections can be found on
        https://developers.google.com/earth-engine/datasets
    coords: list of str
        GPS coordinates in WGS84 [East, North]. Minimum of one set of
        coordinates should be provided to create a point coordinate. If more
        than one set of coordinates is provided, a polygon will be created
    date : str
        Start date of image(s) to be collected in YYYY-MM-DD or YYYY format
    end_date : str, optional
        End date of image(s) to be collected in YYYY-MM-DD or YYYY format
    buffer : int, optional
        If `coords` is a point, a buffer can be provided to create a polygon.
        The buffer is in metres
    bound : bool, optional
        Instead of a circular buffer, request a square bounding box around the
        point based on the buffer size

    Methods
    -------
    preprocess():
        filter, mask, buffer, reduce and/or clip an image collection
    aggregate():
        perform temporal aggregation on an image collection
    map():
        preview an image or image collection
    download():
        download an image or image collection in tif, png or csv format
    """

    def __init__(
        self,
        collection=None,
        coords=None,
        date=None,
        end_date=None,
        buffer=None,
        bound=False,
        config=None,
    ):
        # Stop if minimum requirements are not met
        if config is None and any(a is None for a in [collection, coords, date]):
            raise ValueError(
                "Please supply either a path to a YAML file in 'config', or "
                + "fill in all the required arguments for at least "
                + "'collection', 'coords' and 'date'"
            )
        elif config is not None:
            # Open and aggregate configuration settings into groups
            with open(config, "r") as f:
                # TODO: put into kwargs at some point to clean this up
                yaml_vals = yaml.load(f, Loader=yaml.SafeLoader)

            # Parse settings
            gee_config = yaml_vals["target_sources"]["GEE"]
            gee_process = gee_config["preprocess"]
            try:
                gee_aggregate = gee_config["aggregate"]
            except KeyError:
                pass
            gee_download = gee_config["download"]

            # Class attributes:
            collection = gee_process["collection"]
            if coords is not None:
                coords = gee_process["coords"]
            # If date and endate are provided in YAML, overwrite existing
            try:
                gee_process["date"]
            except KeyError:
                gee_process["date"] = None
            try:
                gee_process["end_date"]
            except KeyError:
                gee_process["end_date"] = None
            use_gee_dates = False
            if gee_process["date"] is not None and gee_process["end_date"] is not None:
                date = gee_process["date"]
                end_date = gee_process["end_date"]
                use_gee_dates = True
            elif gee_process["date"] is not None and gee_process["end_date"] is None:
                # start = str(date[0]) + "-01-01"
                # end_date = str(date[0]) + "-12-31"
                # year_to_range = parse_year_to_range(gee_process["date"])
                date = str(gee_process["date"][0]) + "-01-01"
                end_date = str(gee_process["date"][0]) + "-12-31"
                use_gee_dates = True

            if use_gee_dates is False:
                if len(yaml_vals["target_dates"]) == 1:
                    pass
                elif len(yaml_vals["target_dates"]) > 1:
                    print("Multiple dates provided, using first date for GEE")

                date = str(yaml_vals["target_dates"][0]) + "-01-01"
                end_date = str(yaml_vals["target_dates"][0]) + "-12-31"

            # Set GEE preprocessing attributes to None if not found so that the script
            # doesn't crash
            try:
                gee_process["buffer"]
            except KeyError:
                gee_process["buffer"] = None

            try:
                gee_process["bound"]
            except KeyError:
                gee_process["bound"] = None

            # check dates
            if isinstance(date, datetime.date):
                date = date.strftime("%Y-%m-%d")
            if isinstance(end_date, datetime.date):
                end_date = end_date.strftime("%Y-%m-%d")
            # Ok, store method-specific settings
            self.yaml_vals = yaml_vals
            self.gee_config = gee_config
            self.gee_process = gee_process
            try:
                self.gee_aggregate = gee_aggregate
            except Exception:
                pass
            self.gee_download = gee_download

        # Check that end_date exists, if not, generate exception
        if end_date is None:
            raise ValueError(
                "Please provide an `end_date` argument to define date range"
            )
        # Check that date is not equal to end_date, if so, generate exception
        if date == end_date:
            raise ValueError(
                "Please provide a different `end_date` argument to define date range"
            )
        # Check that collection exists in GEE catalog
        valid = validate_collection(collection)

        # Finalise
        self.collection = collection
        self.coords = coords
        self.date = str(date)
        self.end_date = str(end_date)
        self.buffer = buffer
        self.bound = bound

        # Used for checks:
        if config is not None:
            self.hasconfig = True
        else:
            self.hasconfig = False
        self.ee_image = None
        self.scale = None
        self.minmax = None
        self.image_count = 1
        self.valid = valid

    def preprocess(
        self,
        mask_clouds=True,
        reduce="median",
        spectral=None,
        clip=True,
        **kwargs,
    ):
        """
        Preprocess an Earth Engine Image or ImageCollection

        Obtain image stacks from a Google Earth Engine catalog collection for
        processing. Full support for Sentinel-2, Landsat 5-8, Soil and Landscape
        Grid Australia (CSIRO) and DEM (Geoscience Australia). Preprocessing
        performs server-side filtering, cloud masking, scaling and offsetting,
        calculation of spectral indices and compositing into a single image
        representing, for example, the median, min, max, mean, quantile or
        standard deviation of the images.

        Parameters
        ----------
        mask_clouds : bool, optional
            Performs cloud and shadow masking for Sentinel-2 and Landsat 5-9
            image collections, by default True
        reduce : str, optional
            Composite or reduce an image collection into a single image. A
            comprehensive list of reducers can be viewed from the "ee.Reducer"
            section of the Earth Engine API which also documents their use
            (https://developers.google.com/earth-engine/apidocs/). The most
            common reducers are "min", "max", "minMax", "median", "mean",
            "mode", "stDev" and "percentile",  by default "median"
        spectral : list of str, optional
            Calculate one or more spectral indices via Awesome Spectral Indices
            (https://awesome-ee-spectral-indices.readthedocs.io/en/latest/).
            This is performed automatically by applying the expressions defined
            on the website, by default None
        clip : bool, optional
            Clip the image. This only affects the interactive map view and will
            not influence the data download, by default True

        Returns
        -------
        ee.Image.Image or ee.Image.ImageCollection
            An Earth Engine object which can be further manipulated should the
            user not choose to use other methods in the class.
        """
        utils.msg_info("Running preprocess()")
        # Check if user has provided a config file
        if self.hasconfig is True:
            mask_clouds = self.gee_process["mask_clouds"]
            reduce = self.gee_process["reduce"]
            spectral = self.gee_process["spectral"]
        # Generate area of interest
        if len(self.coords) == 4:
            aoi = ee.Geometry.Rectangle(self.coords)
        elif len(self.coords) == 2:
            aoi = ee.Geometry.Point(self.coords)
        # Is there a buffer? Is a point supplied? Then buffer it
        if self.buffer is not None and len(self.coords) == 2:
            aoi = aoi.buffer(self.buffer)
        if self.bound is True and self.buffer is not None:
            aoi = aoi.bounds()
        # Filter dates
        img = ee.ImageCollection(self.collection).filterBounds(aoi)
        img = img.filterDate(self.date, self.end_date)
        # Check if there are any images by verifying that image bands exist
        # NOT WORKING
        try:
            img.first().bandNames().getInfo()
        except ee.EEException:
            cprint(
                "✘ No images - please verify date range. Processing cancelled",
                "red",
                attrs=["bold"],
            )
        # Count images if reduce is None:
        if reduce is False or reduce is None:
            reduce = None
            with spin("Image collection requested, counting images...") as s:
                image_count = int(img.size().getInfo())
                if image_count > 0:
                    self.image_count = image_count  # store for later use
                else:
                    cprint("✘ No images found, please check date range", "red")
                    return None
                s(1)
        # Scale and offset, mask clouds
        try:
            img = img.scaleAndOffset()
        except Exception:
            pass
        if mask_clouds:
            try:
                with spin("Applying scale, offset and cloud masks...") as s:
                    img = img.maskClouds()
                    s(1)
            except Exception:
                pass
        # Spectral index
        if spectral is not None:
            with spin(f"Computing spectral index: {spectral}") as s:
                try:
                    # Validation: check if spectral index is supported
                    full_list = list(get_indices().keys())
                    spectral_list = (
                        [spectral] if isinstance(spectral, str) else spectral
                    )
                    if not set(spectral_list).issubset(full_list):
                        raise Exception(
                            cprint(
                                "✘ At least one of your spectral indices is not valid. "
                                "Please check the list of available indices at "
                                "https://awesome-ee-spectral-indices.readthedocs.io/en/latest/."
                                " Processing cancelled",
                                "red",
                                attrs=["bold"],
                            )
                        )
                    img = img.spectralIndices(spectral, online=True)
                except Exception:
                    pass
                s(1)
        else:
            pass
        # Function to map to collection
        def clip_collection(image):
            return image.clip(aoi)

        if clip:
            img = img.map(clip_collection)
        # If image is an image collection, limit to 3 samples for stretching pixels
        ee_sample = img.limit(3)
        # Reduce/aggregate
        reducers = ["median", "mean", "sum", "mode", "max", "min", "mosaic"]
        if reduce is None:
            utils.msg_info(f"Selected {image_count} image(s) without aggregation")
        elif reduce in reducers:
            with spin(f"Reducing image pixels by {reduce}") as s:
                func = getattr(img, reduce)
                img = func()
                s(1)
        # Update metadata (TODO: perhaps a better way to do this)
        self.aoi = aoi
        self.reduce = reduce
        self.spectral = spectral
        self.ee_sample = ee_sample
        self.ee_image = img
        utils.msg_success("Google Earth Engine preprocessing complete")
        return img

    def aggregate(self, frequency="month", reduce_by=None, **kwargs):
        """
        Aggregate an Earth Engine Image or ImageCollection by period

        Parameters
        ----------
        frequency : str, optional
            aggregation frequency, either by "day". "week" or "month", by
            default "month"
        """
        utils.msg_info("Running aggregate()")
        if reduce_by is None:
            reducer = ee.Reducer.mean()
        # Check if user has provided a config file
        if self.hasconfig is True:
            frequency = self.gee_aggregate["frequency"]
            reduce_by = self.gee_aggregate["reduce_by"]
            cprint(f"Using ee.Reducer.{reduce_by}", "yellow")
        img = self.ee_image
        # Convert to wxee object
        ts = img.wx.to_time_series()
        cprint("\u2139 Initial aggregate", "blue")
        ts.describe()
        out = ts.aggregate_time(frequency=frequency, reducer=reducer)
        with spin("Calculating new temporal aggregate...") as s:
            out.describe()
            s(1)
        self.ee_image = out

    def map(self, bands=None, minmax=None, palette=None, save_to=None, **kwargs):
        """
        Visualise an Earth Engine Image or ImageCollection on a map

        Parameters
        ----------
        bands : str or list of str, optional
            A string or list of strings representing the bands to be visualised.
        minmax : list of int, optional
            A list of two integers representing the minimum and maximum values.
            If set to None, the min and max values are automatically calculated,
            by default None
        palette : str, optional
            A string representing the name of a palette to be used for map
            colors. Names are accessed from Matplotlib Colourmaps as described
            in https://matplotlib.org/stable/tutorials/colors/colormaps.html. In
            addition, "ndvi", "ndwi" and "terrain" palettes are available. If
            set to None, "viridis" is used, by default None

        Returns
        -------
        geemap.Map
            An interactive map object which can be further manipulated. A
            preview is also genereated.

        Raises
        ------
        ValueError
            If the bands are not valid or not present in the image.
        """
        utils.msg_info("Running map()")
        # Check that preprocess() has been called
        img = self.ee_image
        if img is None:
            print("✘ No image found, please run `preprocess()` before mapping")
            return None
        # Validate that at least one band is selected
        all_bands = get_bandinfo(img)
        if bands is None:
            print("✘ No bands defined - nothing to preview")
            print("\u2139 Please select one or more bands to view image:")
            print(all_bands)
            return None
        else:
            # Just making sure that bands is a list
            bands = [bands] if isinstance(bands, str) else bands
        if not set(bands).issubset(set(all_bands)):
            raise ValueError(
                f"Pattern '{bands}' not found in image. "
                + f"Available bands: {all_bands}"
            )
        # Initialise map
        # SLOW FOR TEMPORAL AGGREGATION, CHECK
        # Band(s) exist, let's filter
        bands = [bands] if isinstance(bands, str) else bands
        img = img.select(bands)
        # Check if geometry is a point and let user know
        if self.aoi.getInfo()["type"] == "Point":
            utils.msg_warn(
                "Looks like geometry is set to a single point with "
                + "no buffer. Plotting anyway..."
            )
        # Create min and max parameters for map
        if minmax is None:
            with spin("Detecting band min and max parameters...") as s:
                # Scale here is just for visualisation purposes
                if len(bands) == 1:
                    minmax = stretch_minmax(
                        self.ee_sample, self.aoi, bands, by="sd", scale=100
                    )
                elif len(bands) > 1:
                    minmax = stretch_minmax(
                        self.ee_sample, self.aoi, bands, by="sd", scale=100
                    )
                s(1)
        param = dict(
            min=minmax[0],
            max=minmax[1],
        )
        Map = geemap.Map()
        # Generate palette if single-band
        if len(bands) == 1:
            if palette is None:
                utils.msg_warn("Palette is set to None, using 'viridis'")
                palette = geemap.get_palette_colors("viridis")
            # add some custom palettes provided by geemap
            elif palette.lower() == "ndvi":
                palette = cm.palettes.ndvi
            elif palette.lower() == "ndwi":
                palette = cm.palettes.ndwi
            elif palette.lower() == "terrain":
                palette = cm.palettes.terrain
            # Generate map layer
            param.update(palette=palette)
            # param.update(region=self.aoi)
            if isinstance(img, ee.image.Image):
                Map.addLayer(img, param, name=bands[0])
            else:
                Map.add_time_slider(img, param, time_interval=3)
                # Map.add_colorbar_branca(paramvis, label=bands[0], transparent_bg=False)
        # Otherwise, generate map without palette
        else:
            if isinstance(img, ee.image.Image):
                Map.addLayer(img, param, name=str(bands).strip("[]"))
            else:
                Map.add_time_slider(img, param, time_interval=3)
        # Add bounding box
        # Map.addLayer(self.aoi, shown=False)
        # Update class attributes
        self.bands = bands
        self.param = param
        self.minmax = minmax
        # For R preview to HTML
        if save_to is not None:
            # Save map html to temp directory
            Map.centerObject(self.aoi, 12)
            Map.to_html(save_to)
        Map.centerObject(self.aoi)
        utils.msg_success("Map generated")
        return Map

    def download(
        self,
        bands=None,
        scale=None,
        outpath=None,
        out_format=None,
        overwrite=False,
        **kwargs,
    ):
        """
        Download an Earth Engine asset to disk and update logtable

        Parameters
        ----------
        bands : str or list of str, optional
            A string or list of strings representing the bands to be visualised.
            If set to None, will check if bands are set in the class. If not,
            the user will be prompted to select one or more bands, by default
            None
        scale : int, optional
            A number representing the scale of the image in meters. If set to
            None, will pick a default scale value of 100 m, by default None
        outpath : str, optional
            A string representing the path to the output directory. If set to
            None, will use the current working directory and add a "downloads"
            folder, by default None
        out_format : str, optional
            One of the following strings: "png", "jpg", "tif". If set to None,
            will use "tif", by default None
        overwrite : boolean, optional
            Overwrite existing file if it already exists, by default False

        Returns
        -------
        None
            Nothing is returned.

        Raises
        ------
        ValueError
            If out_format is not one of 'png', 'jpg', 'tif'.
        """
        utils.msg_info("Running download()")
        # Check if user has provided a config file
        if self.hasconfig is True:
            bands = self.gee_download["bands"]
            scale = self.gee_download["scale"]
            outpath = self.yaml_vals["outpath"]
            out_format = self.gee_download["format"]
            overwrite = self.gee_download["overwrite"]
        # Check that preprocess() has been called
        img = self.ee_image
        if img is None:
            utils.msg_err("No image found, please run `preprocess()` before mapping")
            return None
        # Stop if image is a pixel
        if self.aoi.getInfo()["type"] == "Point":
            utils.msg_warn(
                "Single pixel selected. Did you set a buffer in `collect()`?"
            )
            utils.msg_err("Download cancelled")
            return
        # Stop if out_format is not png, jpg or tif
        if out_format is None:
            # cprint(
            #     "• `out_format` is set to None, downloading as GEOTIFF, 'tif'", "blue"
            # )
            out_format = "tif"
        elif out_format not in ["png", "jpg", "tif"]:
            raise ValueError("out_format must be one of 'png', 'jpg' or 'tif'")
        # Validate that at least one band is selected
        if bands is None:
            try:
                bands = self.bands
            except AttributeError:
                all_bands = get_bandinfo(img)
                utils.msg_err("No bands defined")
                utils.msg_info("Please select one or more bands to download image:")
                print(all_bands)
                return None
        img = img.select(bands)
        utils.msg_info(f"Band(s) selected: {bands}")
        # Throw error if scale is None, i.e. force user to set scale again
        if scale is None:
            utils.msg_warn("Scale not set, using scale=100")
            scale = 100
        # Determine save path
        if outpath is None:
            outpath = generate_dir("downloads")
        else:
            outpath = generate_dir(outpath)
        pathstring = generate_path_string(
            img,
            self.collection,
            self.date,
            self.end_date,
            bands,
            self.reduce,
            scale,
            out_format,
        )
        fullpath = make_path(outpath, pathstring)
        # Download file(s)
        is_tif = out_format.replace(".", "").lower() in ["tif", "tiff"]
        # cprint(f"• Downloading to {outpath}...", "blue")
        if is_tif:
            filenames = download_tif(img, self.aoi, fullpath, scale, overwrite)
            self.filenames = filenames
        self.outpath = outpath
        utils.msg_success("Google Earth Engine download(s) complete")
        return None


def harvest(obj, **kwargs):
    """
    Preprocess, aggregate and download Earth Engine assets by config file
    """
    # TODO: Validate that config file is present
    if obj.hasconfig is False:
        raise Exception("This function requires a config file supplied in `collect()`")
    # Replace coordinates if needed
    if kwargs["coords"] is not None:
        obj.coords = kwargs["coords"]
    obj.preprocess()
    # try:
    #     obj.aggregate()
    # except Exception as e:
    #     print(e)
    obj.download()
    return obj


# :::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
# :::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
# :::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
# :::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
# :::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
# :::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
# Common functions -----------------------------------------------------------
# :::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
# :::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
# :::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
# :::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
# :::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::


def get_indices() -> dict:
    """
    Returns a dictionary of available indices from Awesome Spectral Indices
    """
    with urllib.request.urlopen(
        "https://raw.githubusercontent.com/awesome-spectral-indices/awesome-spectral-indices/main/output/spectral-indices-dict.json"
    ) as url:
        try:
            indices = json.loads(url.read().decode())
        except Exception as e:
            print(e)
    return indices["SpectralIndices"]


def extract_ids(img_collection):
    """
    Extracts the image IDs from an Earth Engine image collection
    """
    with spin("Collecting image ids...") as s:
        count = img_collection.size().getInfo()
        tif_list = []
        for i in range(0, count):
            image = ee.Image(img_collection.toList(count).get(i))
            name = image.get("system:index").getInfo() + ".tif"
            tif_list.append(name)
        s(1)
    return tif_list


def validate_collection(collection):
    """
    Checks whether collection ID string is a STAC in the GEE catalog

    Parameters
    ----------
    collection : string
        A string representing the collection ID

    Returns
    -------
    boolean
        True if collection is in the GEE catalog, False otherwise
    """
    stac_list = sh.ee_stac()
    supported = supported_collections()
    # Check if collection is in STAC and supported
    if collection in stac_list and collection in list(supported.keys()):
        return True
    # If in STAC but not supported, print info and continue
    elif collection in stac_list and collection not in list(supported.keys()):
        utils.msg_warn(f"Collection {collection} is not officially supported.")
        print("  Some preprocessing and aggregation steps are not available")
        return True
    else:
        errmsg = (
            f"Collection {collection} not found in GEE STAC. Please "
            + "check spelling. Processing cancelled"
        )
        utils.msg_err(errmsg)
        return False


def supported_collections():
    """
    A dictionary of supported collections
    """
    supported = {
        "LANDSAT/LT05/C02/T1_L2": "Landsat 5 TM Surface Reflectance",
        "LANDSAT/LE07/C02/T1_L2": "Landsat 7 ETM+ Surface Reflectance",
        "LANDSAT/LC08/C02/T1_L2": "Landsat 8 OLI/TIRS Surface Reflectance",
        "LANDSAT/LC09/C02/T1_L2": "Landsat 9 OLI-2/TIRS-2 Surface Reflectance",
        "COPERNICUS/S2_SR": "Sentinel-2 Surface Reflectance",
        "CSIRO/SLGA": "Soil and Landscape Grid of Australia (SLGA)",
    }
    return supported


def match_collection(collection):
    """
    Match a collection (provided by user) to a supported collection. Not yet
    used.
    """
    supported = supported_collections()
    img = ee.ImageCollection(collection)
    try:
        img.first().get("system:id").getInfo()
    except ee.EEException:
        utils.msg_err(f"The collection {collection} does not exist")
        # TODO: possible suggests
        # cprint("\n".join(list(supported.keys())), "magenta")
        return

    if set([collection]).issubset(supported):
        print(f"Accessing {supported[collection]} images")
    else:
        cprint(
            f"\u2139 Collection {collection} exists but may not fully work "
            + "with Data-Harvester",
            "yellow",
        )
    return None


def get_bandinfo(image):
    """
    Return list of available bands in image
    """
    try:
        bands = image.bandNames().getInfo()
    except AttributeError:
        bands = image.first().bandNames().getInfo()
    return bands


def stretch_minmax(
    ee_image, region, bands, by="percentile", percentile=98, sd=3, scale=None
):
    """
    Calculate min and max values for each band in an image

    Use percentile or standard deviation to generate minimum and maxmimum
    values for Earth Engine image band(s). Useful for visualisation.

    Parameters
    ----------
    ee_image : obj
        Earth Engine image object
    region : obj
        Earth Engine geometry object
    bands : str or list of str
        Band(s) to calculate min and max values for
    by : str, optional
        method to use to calculate min and max values, by default "percentile"
    percentile : int, optional
        Percentile to use to calculate min and max values, by default 98
    sd : int, optional
        Standard deviation to use to calculate min and max values, by default 3
    scale : int, optional
        Scale to use to calculate min and max values, by default None

    Returns
    -------
    list
        A list of min and max values for each band
    """
    try:
        ee_image = ee_image.median()
    except AttributeError:
        pass

    # Filter image to selected bands
    if by == "percentile":
        # Calculate start and end percentiles
        startp = 50 - (percentile / 2)
        endp = 50 + (percentile / 2)

        if not bands:
            names = ee_image.bandNames()
            bands = ee.List(
                ee.Algorithms.If(names.size().gte(3), names.slice(0, 3), names.slice(0))
            )
            bands = bands.getInfo()

        image = ee_image.select(bands)
        geom = region or image.geometry()
        params = dict(geometry=geom, bestEffort=True)
        # Set scale if available
        if scale:
            params["scale"] = scale
        params["reducer"] = ee.Reducer.percentile([startp, endp])
        percentiles = image.reduceRegion(**params)

        def minmax(band):
            minkey = ee.String(band).cat("_p").cat(ee.Number(startp).format())
            maxkey = ee.String(band).cat("_p").cat(ee.Number(endp).format())

            minv = ee.Number(percentiles.get(minkey))
            maxv = ee.Number(percentiles.get(maxkey))
            return ee.List([minv, maxv])

        if len(bands) == 1:
            band = bands[0]
            values = minmax(band).getInfo()
            minv = values[0]
            maxv = values[1]
        else:
            values = ee.List(bands).map(minmax).getInfo()
            minv = [values[0][0], values[1][0], values[2][0]]
            maxv = [values[0][1], values[1][1], values[2][1]]
    if by == "sd":
        ee_image = ee_image.select(bands)
        # Create dictionary
        geom = region or ee_image.geometry()
        params = dict(geometry=geom, bestEffort=True)
        # Set scale if available
        if scale:
            params["scale"] = scale
        params["reducer"] = ee.Reducer.mean()
        mean = ee_image.reduceRegion(**params)
        params["reducer"] = ee.Reducer.stdDev()
        stdDev = ee_image.reduceRegion(**params)

        def min_max(band, val):
            minv = ee.Number(val).subtract(ee.Number(stdDev.get(band)).multiply(sd))
            maxv = ee.Number(val).add(ee.Number(stdDev.get(band)).multiply(sd))
            return ee.List([minv, maxv])

        # Make calculations based on no. of bands used
        if len(bands) == 1:
            band = bands[0]
            values = min_max(band, mean.get(band)).getInfo()
            minv = values[0]
            maxv = values[1]
        else:
            values = mean.map(min_max).select(bands).getInfo()
            minv = [values[bands[0]][0], values[bands[1]][0], values[bands[2]][0]]
            maxv = [values[bands[0]][1], values[bands[1]][1], values[bands[2]][1]]
    return [minv, maxv]


def make_path(dir, filename):
    """
    Create full path to a file
    """
    if dir is None:
        path = filename
        pass
    elif filename is None:
        path = dir
        pass
    else:
        path = os.path.join(dir, filename)
    return path


def generate_path_string(
    ee_image,
    name,
    date,
    end_date=None,
    bands=None,
    reduce=None,
    scale=None,
    ext="tif",
):
    """
    Generate a string to name a file or folder for Earth Engine downloads
    """
    # Clean colletion string
    name = "".join(name.split("/")[0])[:3]
    # Generate date string
    try:
        date = date.replace("-", "")
    except (AttributeError, TypeError):
        pass
    try:
        end_date = end_date.replace("-", "")
    except (AttributeError, TypeError):
        pass
    # Generate band string
    if bands is not None:
        bands = "".join(str(i) for i in bands)
        bands = bands.replace("_", "")
    scale = "".join([str(scale), "m"])
    # The only difference is whether to add extension to string, or not
    if isinstance(ee_image, ee.image.Image):
        out = (
            "_".join(filter(None, ["ee", name, date, end_date, bands, reduce, scale]))
            + "."
            + ext
        )
    else:
        out = "_".join(filter(None, [name, date, end_date, bands, reduce, scale]))

    return out


def generate_dir(dir, subfolder=None):
    """
    Create directory with subfolder if it doesn't exist
    """
    if subfolder is None:
        pass
    else:
        dir = os.path.join(dir, subfolder)
    if not os.path.exists(dir):
        os.makedirs(dir)
    return dir


def pixels_to_bytes(image, scale):
    """
    Convert image pixel information to bytes
    """
    imageDescription = ee.Dictionary(ee.Algorithms.Describe(image))
    bands = ee.List(imageDescription.get("bands"))

    def getBits(band):
        dataType = ee.Dictionary(ee.Dictionary(band).get("data_type"))
        precision = dataType.getString("precision")
        out = ee.Algorithms.If(
            precision.equals("int"),
            intBits(dataType),
            ee.Algorithms.If(precision.equals("float"), 32, 64),
        )
        return out

    def intBits(dataType):
        min = dataType.getNumber("min")
        max = dataType.getNumber("max")
        types = ee.FeatureCollection(
            [
                ee.Feature(None, {"bits": 8, "min": -(2**7), "max": 2**7}),
                ee.Feature(None, {"bits": 8, "min": 0, "max": 2**8}),
                ee.Feature(
                    None,
                    {
                        "bits": 16,
                        "min": -(2**5),
                        "max": 2**5,
                    },
                ),
                ee.Feature(None, {"bits": 16, "min": 0, "max": 2**16}),
                ee.Feature(
                    None,
                    {
                        "bits": 32,
                        "min": -(2**31),
                        "max": 2**31,
                    },
                ),
                ee.Feature(None, {"bits": 32, "min": 0, "max": 2**32}),
            ]
        )
        out = (
            types.filter(ee.Filter.lte("min", min))
            .filter(ee.Filter.gt("max", max))
            .merge(ee.FeatureCollection([ee.Feature(None, {"bits": 64})]))
            .first()
            .getNumber("bits")
        )
        return out

    bits = ee.Number(bands.map(getBits).reduce(ee.Reducer.sum()))
    pixelCount = (
        image.geometry()
        .bounds()
        .area(scale)
        .divide(ee.Number(scale).pow(2))
        .sqrt()
        .ceil()
        .pow(2)
    )
    return bits.divide(8).multiply(pixelCount).ceil()


def convert_size(size_bytes):
    """
    Convert size in bytes to appropriate unit.

    Source https://stackoverflow.com/a/14822210
    """
    if size_bytes == 0:
        return "0B"
    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return "%s %s" % (s, size_name[i])


def download_tif(image, region, path, scale, crs="EPSG:4326", overwrite=True):
    """
    Download image to local folder as GeoTIFF

    Parameters
    ----------
    image : obj
        ee.Image or ee.ImageCollection object
    region : dict
        ee.Geometry object
    path : str
        Path to save image to
    scale : int
        Scale in metres to define the image resolution
    crs : str, optional
        Coordinate reference system, by default "EPSG:4326"
    """
    if isinstance(image, ee.image.Image):
        filename = os.path.basename(path)
        # Check if path already exists and don't download if it does
        if os.path.exists(path) and overwrite:
            utils.msg_warn(f"{filename} already exists, skipping download")
            return filename
        # Otherwise download image
        with suppress():
            # hide tqdm if disable=True
            tqdm.__init__ = partialmethod(tqdm.__init__, disable=True)
            # Get filename from path

            with spin(f"Downloading {filename}") as s:
                geemap.download_ee_image(
                    image=image,
                    region=region,
                    filename=path,
                    crs="EPSG:4326",
                    scale=scale,
                )
                s(1)
        # final_size = convert_size(os.path.getsize(path))
        # cprint(f"✔ File saved as {path} [final size {final_size}]", "green")
        return filename
    else:
        file_list = extract_ids(image)
        geemap.download_ee_image_collection(
            collection=image,
            out_dir=path,
            region=region,
            crs="EPSG:4326",
            scale=scale,
        )
        # cprint(f"✔ Files saved to {path}", "green")
    return file_list


def preview_tif(image, bands, path, **kwargs):
    """
    Preview downloaded GeoTIFF image
    """
    bands = [bands] if isinstance(bands, str) else bands
    # Generate palette
    try:
        kwargs["palette"]
    except KeyError:
        kwargs["palette"] = "RdYlGn"
    if len(bands) == 1:
        if isinstance(image, ee.image.Image):
            cprint(
                "• Previewing downloaded image:",
                "blue",
            )
            preview = rioxarray.open_rasterio(path)
            preview.plot(size=8, cmap=kwargs["palette"])
        else:
            preview.plot.imshow(size=4, robust=True)
    else:
        cprint(
            "✘ Sorry, preview of multiple rasters not yet available",
            "red",
        )


def parse_year_to_range(date):
    """Convert single-year value to ymd range for the same year"""
    start = str(date[0]) + "-01-01"
    end_date = str(date[0]) + "-12-31"
    return start, end_date
