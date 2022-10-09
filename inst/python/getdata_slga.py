"""
Python script to download data from Soil and Landscape Grid of Australia (SLGA).

Core functionality:
- Retrieval of WCS capability  with function get_capabilities()
- automatic download SLGA data for given depth range and layer(s) via Web Coverage Service (WCS)
- clip data to custom bounding box
- save data as multi-band geotiff
- plot data as map

The SLGA layers and metadata are described as dictionary in the module function get_slgadict()
and the respective licensing and attribution are availabe with the module function getdict_license()

More details about the SLGA data and attributions can be found here:
https://www.clw.csiro.au/aclep/soilandlandscapegrid/ProductDetails-SoilAttributes.html

This package is part of the Data Harvester project developed for the Agricultural Research Federation (AgReFed).

Copyright 2022 Sydney Informatics Hub (SIH), The University of Sydney

This open-source software is released under the LGPL-3.0 License.

Author: Sebastian Haan
"""

import os
from owslib.wcs import WebCoverageService
import rasterio
from rasterio.plot import show
import utils
from utils import spin

# logger setup
import write_logs
import logging


def get_slgadict():
    """
    Get dictionary of SLGA data.

    The Soil Facility produced a range of digital soil attribute products.
    Each product contains six digital soil attribute maps, and their upper and lower confidence limits,
    representing the soil attribute at six depths: 0-5cm, 5-15cm, 15-30cm, 30-60cm, 60-100cm and 100-200cm.
    These depths are consistent with the specifications of the GlobalSoilMap.net project (http://www.globalsoilmap.net/).
    The digital soil attribute maps are in raster format at a resolution of 3 arc sec (~90 x 90 m pixels).

    Period (temporal coverage; approximately): 1950-2013;
    Spatial resolution: 3 arc seconds (approx 90m);
    Data license : Creative Commons Attribution 3.0 (CC By);
    Target data standard: GlobalSoilMap specifications;
    Format: GeoTIFF.

    Run function get_capabilities(url) to update dictionary

    Returns
    -------
    slgadict : dictionary of National Soil Map data
    """
    slgadict = {}
    slgadict["title"] = "SLGA"
    slgadict["description"] = "National Soil and Landscape Grid of Australia"
    slgadict["crs"] = "EPSG:4326"
    slgadict["bbox"] = [
        112.9995833334,
        -44.0004166670144,
        153.999583334061,
        -10.0004166664663,
    ]
    slgadict["resolution_arcsec"] = 3
    slgadict["depth_min"] = 0
    slgadict["depth_max"] = 200
    slgadict["layers_url"] = {
        "Bulk_Density": "https://www.asris.csiro.au/ArcGIS/services/TERN/BDW_ACLEP_AU_NAT_C/MapServer/WCSServer",
        "Organic_Carbon": "https://www.asris.csiro.au/ArcGIS/services/TERN/SOC_ACLEP_AU_NAT_C/MapServer/WCSServer",
        "Clay": "https://www.asris.csiro.au/ArcGIS/services/TERN/CLY_ACLEP_AU_NAT_C/MapServer/WCSServer",
        "Silt": "https://www.asris.csiro.au/ArcGIS/services/TERN/SLT_ACLEP_AU_NAT_C/MapServer/WCSServer",
        "Sand": "https://www.asris.csiro.au/ArcGIS/services/TERN/SND_ACLEP_AU_NAT_C/MapServer/WCSServer",
        "pH_CaCl2": "https://www.asris.csiro.au/ArcGIS/services/TERN/PHC_ACLEP_AU_NAT_C/MapServer/WCSServer",
        "Available_Water_Capacity": "https://www.asris.csiro.au/ArcGIS/services/TERN/AWC_ACLEP_AU_NAT_C/MapServer/WCSServer",
        "Total_Nitrogen": "https://www.asris.csiro.au/ArcGIS/services/TERN/NTO_ACLEP_AU_NAT_C/MapServer/WCSServer",
        "Total_Phosphorus": "https://www.asris.csiro.au/ArcGIS/services/TERN/PTO_ACLEP_AU_NAT_C/MapServer/WCSServer",
        "Effective_Cation_Exchange_Capacity": "https://www.asris.csiro.au/ArcGIS/services/TERN/ECE_ACLEP_AU_NAT_C/MapServer/WCSServer",
        "Depth_of_Regolith": "https://www.asris.csiro.au/ArcGIS/services/TERN/DER_ACLEP_AU_NAT_C/MapServer/WCSServer",
        "Depth_of_Soil": "https://www.asris.csiro.au/ArcGIS/services/TERN/DES_ACLEP_AU_NAT_C/MapServer/WCSServer",
    }
    return slgadict


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

    # show image with matplotlib
    # img = data.read(1)
    # plt.imshow(img, cmap='viridis')
    # plt.colorbar()


def get_capabilities(url):
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

    # Create WCS object
    wcs = WebCoverageService(url, version="1.0.0")

    # URL address for national bulk density layer
    # url_bd = "https://www.asris.csiro.au/ArcGIS/services/TERN/BDW_ACLEP_AU_NAT_C/MapServer/WCSServer?SERVICE=WCS&REQUEST=GetCapabilities"
    # url_bd = "https://www.asris.csiro.au/ArcGIS/services/TERN/BDW_ACLEP_AU_NAT_C/MapServer/WCSServer"

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


def get_wcsmap(url, identifier, crs, bbox, resolution, outfname):
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
    filename = outfname.split(os.sep)[-1]
    if os.path.exists(outfname):
        utils.msg_warn(f"{filename} already exists, skipping download")
        # logging.warning(f"\u25b2 Download skipped: {filename} already exists")
        # logging.info(f"  Location: {outfname}")

        return False
    else:
        with spin(f"Downloading {filename}") as s:
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
            # timeout=30)
            s(1)

        # Save data
        with open(outfname, "wb") as f:
            f.write(data.read())
        return True


def depth2identifier(depth_min, depth_max):
    """
    Get identifiers that correspond to depths and their corresponding confidence interval identifiers
    that lie within the depth range depth_min to depth_max.

    Parameters
    ----------
    depth_min : minimum depth [cm]
    depth_max : maximum depth [cm]

    Returns
    -------
    identifiers : layer identifiers
    identifiers_ci_5pc : identifiers for confidence interval 5%
    identifiers_ci_95pc : identifiers for confidence interval 95%
    depth_lower : lower depth of interval
    depth_upper : upper depth of interval
    """
    depth_intervals = [0, 5, 15, 30, 60, 100, 200]
    identifiers = []
    identifiers_ci_5pc = []
    identifiers_ci_95pc = []
    depths_lower = []
    depths_upper = []
    # Loop over depth intervals
    for i in range(len(depth_intervals) - 1):
        if (depth_min <= depth_intervals[i]) & (depth_max >= depth_intervals[i + 1]):
            identifiers.append(str(3 * i + 1))
            identifiers_ci_5pc.append(str(3 * i + 3))
            identifiers_ci_95pc.append(str(3 * i + 2))
            depths_lower.append(depth_intervals[i])
            depths_upper.append(depth_intervals[i + 1])
    return (
        identifiers,
        identifiers_ci_5pc,
        identifiers_ci_95pc,
        depths_lower,
        depths_upper,
    )


def identifier2depthbounds(depths):
    """
    Get min and max depth of list of depth strings

    Parameters
    ----------
    depth_list: list of depth

    Returns
    -------
    min depth
    max depth
    """
    depth_options = ["0-5cm", "5-15cm", "15-30cm", "30-60cm", "60-100cm", "100-200cm"]
    depth_intervals = [0, 5, 15, 30, 60, 100, 200]
    # Check first if entries valid
    for depth in depth_options:
        assert (
            depth in depth_options
        ), f"depth should be one of the following options {depth_options}"
    # find min and max depth
    ncount = 0
    for i in range(len(depth_options)):
        if depth_options[i] in depths:
            depth_max = depth_intervals[i + 1]
            if ncount == 0:
                depth_min = depth_intervals[i]
            ncount += 1
    assert ncount == len(depths), f"ncount = {ncount}"
    return depth_min, depth_max


def get_slga_layers(
    layernames,
    bbox,
    outpath,
    resolution=3,
    depth_min=0,
    depth_max=200,
    get_ci=True,
    verbose=False,
):
    """
    Download layers from SLGA data server and saves as geotif.

    Parameters
    ----------
    layernames : list of layer names
    bbox : bounding box [min, miny, maxx, maxy] in
    resolution : resolution in arcsec (Default: 3 arcsec ~ 90m, which is native resolution of SLGA data)
    depth_min : minimum depth (Default: 0 cm)
    depth_max : maximum depth (Default: 200 cm, maximum depth of SLGA data)
    outpath : output path

    Returns
    -------
    fnames_out : list of output file names

    TBD: check that Request image size does not exceeds allowed limit. Set Timeout?
    """

    # Logger setup
    if verbose:
        write_logs.setup(level="info")
    else:
        write_logs.setup()

    # Check if layernames is a list
    if not isinstance(layernames, list):
        layernames = [layernames]

    # Check if outpath exist, if not create it
    os.makedirs(outpath, exist_ok=True)

    # If the resolution passed is None, set to native resolution of datasource
    if resolution is None:
        resolution = get_slgadict()["resolution_arcsec"]

    # Get SLGA dictionary
    slgadict = get_slgadict()
    layers_url = slgadict["layers_url"]

    # Convert resolution from arcsec to degree
    resolution_deg = resolution / 3600.0

    # set crs
    crs = "EPSG:4326"

    # Get depth identifiers for layers
    (
        identifiers,
        identifiers_ci_5pc,
        identifiers_ci_95pc,
        depth_lower,
        depth_upper,
    ) = depth2identifier(depth_min, depth_max)

    fnames_out = []
    # Loop over layers
    for layername in layernames:
        # Get layer url
        layer_url = layers_url[layername]
        # logging.print(f"Downloading {layername}...")
        for i in range(len(identifiers)):
            identifier = identifiers[i]
            # Get layer name
            layer_depth_name = f"SLGA_{layername}_{depth_lower[i]}-{depth_upper[i]}cm"
            # Layer fname
            fname_out = os.path.join(outpath, layer_depth_name + ".tif")
            # download data
            dl = get_wcsmap(layer_url, identifier, crs, bbox, resolution_deg, fname_out)
            # if dl is True:
            #     print(f"✔ {layer_depth_name}")
            # logging.print(f"✔ | {layer_depth_name}")
            # logging.info(f"  | saved to: {fname_out}")
            fnames_out.append(fname_out)
        if get_ci:
            # logging.info(f"Downloading confidence intervals for {layername}...")
            for i in range(len(identifiers)):
                # 5th percentile
                identifier = identifiers_ci_5pc[i]
                # Get layer name
                layer_depth_name = (
                    f"SLGA_{layername}_{depth_lower[i]}-{depth_upper[i]}cm"
                )
                # Layer fname
                fname_out = os.path.join(outpath, layer_depth_name + "_5percentile.tif")
                # download data
                get_wcsmap(layer_url, identifier, crs, bbox, resolution_deg, fname_out)
                # 95th percentile
                identifier = identifiers_ci_95pc[i]
                # Get layer name
                layer_depth_name = (
                    f"SLGA_{layername}_{depth_lower[i]}-{depth_upper[i]}cm"
                )
                # Layer fname
                fname_out = os.path.join(
                    outpath, layer_depth_name + "_95percentile.tif"
                )
                # download data
                dl = get_wcsmap(
                    layer_url, identifier, crs, bbox, resolution_deg, fname_out
                )
                # if dl is True:
                # print(f"✔ {layer_depth_name} CIs")
                # logging.print(f"✔ {layer_depth_name} CIs")
                # logging.info(f"  saved to: {outpath}")
    # logging.print("SLGA download(s) complete")
    return fnames_out


### test functions ###


def test_wcs():

    layername = "Bulk_Density"
    # Get SLGA dictionary
    slgadict = get_slgadict()
    # get layer url
    layers_url = slgadict["layers_url"]
    url = layers_url[layername]
    # url = "https://www.asris.csiro.au/ArcGIS/services/TERN/BDW_ACLEP_AU_NAT_C/MapServer/WCSServer"

    # Get capabilities
    keys, titles, descriptions, bboxs = get_capabilities(url)

    # define bounding box for retrieval (simple test here for ~ half of Australia)
    bbox = (130, -44, 153.9, -11)
    # define resolution (in arcsec per pixel since crs is in WGS84).
    # Note that there is a request size limit for the WCS service.
    resolution = 50
    # define output file name
    outpath = "result_slga_testfunction"

    # Get data for first layer depth
    fnames_out = get_slga_layers(
        "Bulk_Density", bbox, outpath, resolution, depth_min=0, depth_max=5
    )

    # crs = 'EPSG:4326' # WGS84
    # Get data (here only for first layer)
    # identifier = '1'
    # fname_out = 'result_slga_testfunction.tif'
    # get_wcsmap(url, identifier, crs, bbox, resolution / 3600., fname_out)

    # Show data
    plot_raster(fnames_out)
