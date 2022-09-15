#!/bin/python
"""

Utility functions for for temporal processing.

--Function List, in order of appearence--

combine_rasters_temporal: Concatenates files by time returns xarray.
aggregate_temporal: Aggregates xarrays by specified function and time period.

"""

import numpy as np
import pandas as pd
import rioxarray
import xarray as xr


def combine_rasters_temporal(file_list, channel_name='band', attribute_name='long_name'):
    """
    Combines multiple tif files into single xarray object. Assumes files are in
    temporal order, and additional channels contain sequential time step data.
    Also assumes files are of the same shape (x,y,t).

    Example:
    file_list = ['../data/mvp_daily_rain_silo/daily_rain_2017_cropped.tif',
             '../data/mvp_daily_rain_silo/daily_rain_2018_cropped.tif']

    xdr = combine_rasters_temporal(file_list, channel_name='band',attribute_name='long_name')

    Parameters
    ----------
    file_list : list of filename strings in date order to concatenate.
        Expected to be of the form "x,y" or "x,y,z1"
    channel_name : string of coordinate dimension to concatentate (band, time,
        etc). Check options with rioxarray.open_rasterio('filename').coords
    attribute_name : string name of rioxarray attribute holding a time/date
        label. Check with rioxarray.open_rasterio('filename').attrs

    Returns
    -------
    xdr : xarray object of x,y,time, with approriate metadata.

    """
    print("Concatenating",channel_name,"and",attribute_name,"over",file_list)
    # file_list = glob(os.path.join(data_dir, '*.tif'))

    # Append all data/channels, collect metadata lists
    array_list = []
    attrs = ()
    first=True
    for x in file_list:
        xds = rioxarray.open_rasterio(x)

        if channel_name not in xds.coords:
            raise ValueError(channel_name+" not a channel in the raster "+ x+" Options are",[t for t in xds.coords])
            return(None)

        if attribute_name not in xds.attrs:
            raise ValueError(attribute_name+" not an attribute in the raster "+x+" Options are",[t for t in xds.attrs])
            return(None)

        array_list.append(xds)
        attrs = attrs + xds.attrs[attribute_name]
        if first==True:
            coords = xds[channel_name].values

            first=False
        else:
            coords = np.append(coords,xds[channel_name].values+coords[-1])


    xdr = xr.concat(array_list,channel_name)
    # print(agg,coords,attrs)
    # xdr = xdr.assign_attrs({attr: attrs})
    xdr = xdr.assign_coords({channel_name: np.array(pd.to_datetime(attrs))})
    xdr = xdr.rename({channel_name:"time"})
    del xdr.attrs[attribute_name]

    return xdr


def aggregate_temporal(xdr,period='yearly',agg=['mean'],outfile='temporal_agg'):
    """
    Make a data aggregation (mean, median, sum, etc) through time on an xarray.
    Expects xarray coordinates to be x, y, time. Saves every aggregation for
    every time period as its own tif file.

    Example:
    file_list = ['../data/mvp_daily_rain_silo/daily_rain_2017_cropped.tif',
         '../data/mvp_daily_rain_silo/daily_rain_2018_cropped.tif']

    xdr = combine_rasters_temporal(file_list, channel_name='band',attribute_name='long_name')

    outfname_list, agg_list = aggregate_temporal(
        xdr,period=100,agg=['mean','sum'],outfile='temporal_agg')

    Parameters
    ----------
    xdr : xarray object of x,y,time
    period : string or int. Time period to perform aggregation,
        'yearly', 'monthly', or number of periods to aggregate over.
    agg: list of strings. Choice of aggregation methods to apply of
        ['mean','median','sum','perc95','perc5']
    outfile : string. Prefix of output file name.

    Returns
    -------
    outfname_list : list of strings of output file names
    agg_list : list of strings of aggregation methods

    """

    # Check the aggregation methods are okay
    agg_types = ['mean', 'median', 'sum', 'perc95', 'perc5', 'max', 'min']
    aggcheck = [a for a in agg if a in agg_types]
    if aggcheck is None:
        raise ValueError("Invalid Aggregation type. Expected any of: %s" % agg_types)
    else:
        print("Finding", aggcheck, " out of possible", agg_types)
        print("for",period," period.")


    # Group by the appropriate time period
    if period=='yearly':
        xdr_groups = xdr.groupby('time.year')

    elif period=='monthly':
        xdr_groups = xdr.groupby('time.month')

    elif type(period)==int:
        bins = int(np.floor(len(xdr)/period))
        xdr_groups = xdr.groupby_bins('time', bins)
        # indexname='time_bins'

    else:
        raise ValueError("Invalid temporal period. Expected any of: 'yearly', 'monthly', or an integer period")


    #What is more efficient? Make calcs on whole dataframe or on each group?

    #Make ALL agg calcs (and only keep the requested ones later)
    aggdict = {}
    aggdict['mean'] = xdr_groups.mean()
    aggdict['median'] = xdr_groups.median()
    aggdict['sum'] = xdr_groups.sum()
    aggdict['perc95'] = xdr_groups.quantile(q=0.95)
    aggdict['perc5'] = xdr_groups.quantile(q=0.05)
    aggdict['max'] = xdr_groups.max()
    aggdict['min'] = xdr_groups.min()

    #Keep track of the names of all files produced
    outfname_list = []
    agg_list = []

    #For all the different aggregation methods
    for a in aggcheck:
        #For each period of time in each of the groups, save it out!
        for p in aggdict[a]:

            #Each temporal grouping results in different group labels
            if period=='yearly': label=str(p['year'].values)
            elif period=='monthly': label=str(p['month'].values).zfill(2)
            elif type(period)==int: label=str(p['time_bins'].values)[1:11]

            p.rio.to_raster(outfile+"_"+a+"_"+label+".tif")
            outfname_list.append(outfile+"_"+a+"_"+label+".tif")
            agg_list.append(a)

            print(a,"of", label, "saved in:", outfile+"_"+a+"_"+label+".tif")

    return outfname_list, agg_list





#def temporal_aggregate_multiband(file_list=None, data_dir=None, agg=['mean'],
#    outfile='aggregation', timesteps=1):
    """
    NOTE: NOT ALL IMPLEMENTED!!! Specifcally multiband data. But I don't think
    we want to deal with that, as it is already accounted for previously? Maybe.

    Aggregates over multiple files but keeps channels independently.
    Results are written to new tif files.

    This function should

    dates of the from "yyyy-mm-dd"
    rolling mean

    Unit of measurment you are working in seconds, daily, monthly, yearly (or integers)
    Time steps of channels (e.g. 12xmonthly)
    time steps of files (each file represents X length of time)
    time steps of aggregation (e.g. average monthly)
    time steps of



    Aggregrates over multiple files and over all channels
    and writes results to new tif file(s).

    Step 1: combine files (assumes consistent times and start finish points)
    Step 2: roll data into outtime chunks
    Step 3: perform aggregation on chunks

    e.g. aggregate daily rainfall data for each month (for the duration of the files.)
    e.g. aggregate monthly temperature data over a year (for the duration of the files.)

    e.g. aggregate common months over multiple years, average rainfall in July from 2015 to 2020


    Takes a stream of temporal data in a particular time increment and converts
    to a new time-increment by averaging.
    """
