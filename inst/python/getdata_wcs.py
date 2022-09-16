"""
Python test script to get data from geospatial Web Coverage Service (WCS) server
using user-specified resolution, crs and bounding box

See WCS layer retrieval https://geopython.github.io/OWSLib/usage.html#wcs
and https://www.mapserver.org/ogc/wcs_server.html

Here tested with CSIRO TERN National Bulk Density layer
see https://www.asris.csiro.au/ArcGIS/services/TERN/BDW_ACLEP_AU_NAT_C/MapServer/WCSServer?SERVICE=WCS&REQUEST=GetCapabilities


TBD:
- exception handler in case of error or server is down, such as proxy error (502 Server Error)

Author: Sebastian Haan
"""

import os
from owslib.wcs import WebCoverageService
import rasterio
from rasterio.plot import show
import matplotlib.pyplot as plt


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
        title_list.append(wcs[key].abstract)
        print(f"bounding box: {wcs[key].boundingboxes}")
        bbox_list.append(wcs[key].boundingboxes)
        print("")

    return keys, title_list, description_list, bbox_list


def get_wcsmap(outfname, identifier, crs, bbox, resolution, url):
    """
    Download and save geotiff from WCS layer

    Parameters
    ----------
    outfname : str
        output file name
    identifier : str
        layer identifier
    crs : str
        layer crs
    bbox : list
        layer bounding box
    resolution : int
        layer resolution in arcsec
    url : string
        url of wcs server

    """
    # TBD: get capabilities first and check if input options are valid (e.g. bbox within layer)
    # Get data
    wcs = WebCoverageService(url, version="1.0.0")
    data = wcs.getCoverage(
        identifier,
        format="GeoTIFF",
        bbox=bbox,
        crs=crs,
        resx=resolution / 3600,
        resy=resolution / 3600,
    )

    # Save data
    with open(outfname, "wb") as f:
        f.write(data.read())


if __name__ == "__main__":
    # URL address for national bulk density layer
    # Bulk Density layer
    # url = "https://www.asris.csiro.au/ArcGIS/services/TERN/BDW_ACLEP_AU_NAT_C/MapServer/WCSServer"

    # organic carbon layer
    url = "https://www.asris.csiro.au/ArcGIS/services/TERN/SOC_ACLEP_AU_NAT_C/MapServer/WCSServer"

    # Get capabilities
    keys, titles, descriptions, bboxs = get_capabilities(url)

    #### SETTINGS ####
    # TBD: These settings and url should be read from settings yaml file
    # Get data (here only for first layer)
    identifier = "1"
    crs = "EPSG:4326"  # WGS84
    # define bounding box for retrieval (simple test here for entire Australia)
    bbox = (114, -44, 153.9, -11)
    # define resolution (in arcsec per pixel since crs is in WGS84)
    resolution = 100
    # define output file name
    fname_out = "SLGA_OC_1-5cm_AU.tif"

    # Get data
    get_wcsmap(fname_out, identifier, crs, bbox, resolution)

    # Show data
    plot_raster(fname_out)
