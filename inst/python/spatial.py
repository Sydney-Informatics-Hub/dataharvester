#!/bin/python
"""

Utility functions for for spatial processing.

--Function List, in order of appearence--

_points_in_circle(internal): Return all points whose indices are within a given
    circle.
_coreg_buffer(internal): Queries values of a raster around a point buffer
    region.
raster_buffer: Given a longitude,latitude point, a raster file, and a buffer
    region, find the values of all points in circular buffer.
_get_features(internal): Parse features from GeoDataFrame format to Rasterio
    format
_coreg_polygon(internal): Crops a raster to a polygon shape.
raster_polygon_buffer: Given list of longitudes and latitudes defining a
    polygon, crop raster file, return the values of all points in the polygon.
"""

from glob import glob
import os
import json

import rasterio
from rasterio.mask import mask
from rasterio.warp import calculate_default_transform, reproject, Resampling
from rasterio.plot import show

import numpy as np
import pandas as pd
import geopandas as gpd

from pyproj import CRS
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.ticker import FormatStrFormatter

from numba import jit

import utils

from shapely.geometry import Polygon
from fiona.crs import from_epsg
import json


@jit(nopython=True)
def _points_in_circle(i0, j0, r, xlen, ylen):
    """
    A generator to return all points whose indices are within a given circle.
    http://stackoverflow.com/a/2774284
    Warning: If a point is near the the edges of the raster it will not loop
    around to the other side of the raster!
    We yield indexs of points, so this function may be sped up without the
    need for passing data matiricies back and forth.

    INPUTS
    i0: x index column locator centre point
    j0: y index row locator centre point
    r: radius of circle in pixel/index units
    xlen: no. columns of data array.
    ylen: no. rows of data array.

    RETURNS
    generator of tuple containing x-y array index values.

    """
    def intceil(x):
        return int(np.ceil(x))

    for i in range(intceil(i0-r), intceil(i0+r)):
        ri = np.sqrt(r**2-(i-i0)**2)
        for j in range(intceil(j0-ri), intceil(j0+ri)):
            if (i >= 0 and i < xlen) and (j >= 0 and j < ylen):
                # yield arr[i][j]
                yield((i, j))


def _points_in_polygon(i0, j0, polygon):
    # For each point in arr, check if it is inside polygon.
    # Not implemented, or required. Use _coreg_polygon
    pass


def _coreg_buffer(i0, j0, data, region):
    """
    Coregisters a point with a buffer region of a raster.

    INPUTS
    i0: column-index of point of interest
    j0: row-index of point of interest
    data: two-dimensional numpy array (raster)
    region: integer radius, same units as data resolution.

    RETURNS
    pts: all values from array within region
    """

    if (type(region) == float) or (type(region) == int):
        pts_iterator = _points_in_circle(
                            i0, j0, region, len(data[:, 0]), len(data[0, :]))

    else:
        print("This method only uses circular buffers defined by a radius. \
            For buffers defined by a polygon use _coreg_polygon. \
            ")

    # Convert list of returned tuples to indexes readable by the data array.
    pts = tuple(zip(*list(pts_iterator)))

    return data[pts]


def raster_buffer(long, lat, raster, buffer):
    """
    given a longitude,latitude point, a raster file, and a buffer region,
        return the value values of all points in circular buffer.

    INPUTS:
    long: longitude point of interest
    lat: latitude point of interest
    raster: file path/name (as string)
    buffer: integer, raster array pixel units to return values for

    RETURNS
    values: list of raster array values around point of interest.
    """
    print("Opening:", raster)
    # raster = gdal.Open(raster)
    raster = rasterio.open(raster)

    # Get the transformation crs data
    # gt = raster.GetGeoTransform()
    gt  = raster.transform

    # Interogate the tiff file as an array
    # This will only be the first band, usally multiband has same index.
    # arr = raster.GetRasterBand(1).ReadAsArray()
    arr = raster.read(1)

    # FIXME Check the number of bands and print a warning if more than 1

    # Shape of raster
    print("Raster pixel size:", np.shape(arr))

    # get row/column index of point
    point = utils._get_coords_at_point(gt, long, lat)

    # get values of data array at the buffer-index locations
    values = _coreg_buffer(point[0], point[1], arr, buffer)

    return(values)


def _get_features(gdf):
    """
    Function to parse features from GeoDataFrame in such a manner that
        rasterio wants them

    gdf: geodataframe of a geometry polygon.
    """
    return [json.loads(gdf.to_json())['features'][0]['geometry']]


def _coreg_polygon(data, polygon):
    """
    Crops a raster to a polygon shape.

    INPUTS
    data: gdal raster object.
    polygon: Shapely Polygon defining area to crop.

    RETURNS
    out_img: Returns array of values inside the polygon.
    """
    geo = gpd.GeoDataFrame({'geometry': polygon}, index=[0], crs=from_epsg(4326))
    geo = geo.to_crs(crs=data.crs.data)
    coords = _get_features(geo)
    out_img, _ = mask(data, shapes=coords, crop=True)

    return(out_img)


def raster_polygon_buffer(lngs, lats, raster):
    """
    Given a list of longitudes and latitudes that define a polygone, crop a
        raster file, and return the values of all points in the polygon.

    INPUTS:
    lngs: list of longitudes
    lats: list of latitudes
    raster: file path/name (as string) of raster

    RETURNS
    values: list of raster array values inside polygon.
    """
    if (len(lngs) != len(lats)):
        raise ValueError("Longitude and Latitude list should be equal in length\
            representing pairs of points defining a polygon.")

    print("Opening:", raster)
    # raster = gdal.Open(raster)
    raster = rasterio.open(raster)

    # get row/column index of point
    polygon = Polygon(list(zip(lngs, lats)))

    # get values of data array at the buffer-index locations
    values = _coreg_polygon(raster, polygon)

    return(values)
