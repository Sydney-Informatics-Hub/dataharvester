# Validate YAML settings file

"""
# How to: 
import validate_settings
validate_settings.validate(fname_settings)

"""

import yaml
import datetime

# logger setup
import write_logs
import logging

# import AgReFed DataHarvester dictionaries
from getdata_slga import get_slgadict
from getdata_silo import get_silodict
from getdata_dea import get_deadict
from getdata_radiometric import get_radiometricdict
from getdata_landscape import get_landscapedict
from getdata_dem import get_demdict

# Set date constraints
currentDateTime = datetime.datetime.now()
current_year = currentDateTime.date().year
min_year = 1970


def check_schema(settings):
    """
    Validate Schema
    """
    conf_schema = {
        'infile': str,
        'outpath': str,
        'colname_lat': str,
        'colname_lng': str,
        'target_bbox': [list, tuple, str, None],
        'target_dates': list,
        'target_res': [float, int],
        'target_sources': dict,
    }
    for conf in list(settings.keys()):
        if conf not in list(conf_schema.keys()):
            print(f'"{conf}" key not in settings schema')
            return False
        if type(conf_schema[conf]) == str:
            if not type(settings[conf]) == conf_schema[conf]:
                print(f'type {dtype(settings[conf])} not valid for "{conf}"')
                print(f'Need to be {conf_schema[conf]}')
                return False
        elif type(conf_schema[conf]) == list:
            if not type(settings[conf]) in conf_schema[conf]:
                print(f'Dtype {type(settings[conf])} not valid for "{conf}"')
                print(f'Need to be one of: {conf_schema[conf]}') 
                return False
    return True


def check_schema2(settings):
    """
    Validate Schema with package schema

    Requirements: schema
    """
    from schema import Schema, Or, Optional
    conf_schema = Schema({
        'infile': str,
        'outpath': str,
        'colname_lat': str,
        'colname_lng': str,
        'target_bbox': Or(list, tuple, '', None),
        'target_dates': list,
        'target_res': Or(float, int),
        'target_sources': {
            Optional('DEA'): list,
            Optional('DEM'): list,
            Optional('Landscape'): list,
            Optional('Radiometric'): list,
            Optional('SILO'): dict,
            Optional('SLGA'): dict,
            Optional('GEE'): dict,
        }
    })
    try:
        conf_schema.validate(settings)
        return True
    except SchemaError:
        return False


def check_target_dates(dates):
    """
    Validate date range
    """
    for date in dates:
        if (date < min_year):
            print(f'{date} in target_dates must be at least {min_year}')
            return False
        if (date > current_year):
            print(f'{date} in target_dates can not be in the future')
            return False
    return True


def check_target_size(bbox, target_res, nmax_pixels = 1e8):
    """
    Validate bounding box and check number of raster pixels

    INPUT
    -----
    bbox: list, target bounding box
    target_res: float or int, target resolution
    nmax_pixels: maximum number of raster pixels for target image (nmax = nx * ny)
    """
    if (bbox != None) & (bbox != ''):
        # Check if bbox is correct order: [left, bottom, right, top]
        assert len(bbox) == 4, 'Length of Bounding box must be 4' 
        assert bbox[2] > bbox[0], 'Bounding box[0] must be smaller than box[2]'
        assert bbox[3] > bbox[1], 'Bounding box[1] must be smaller than box[3]'
        # Estimate number of raster pixel
        nx = round(3600 * (bbox[2] - bbox[0]) / target_res)
        ny = round(3600 * (bbox[3] - bbox[1]) / target_res)
        npix = nx * ny
        if npix > nmax_pixels:
            print(f'Number of pixels  of requested image ({npix}) is larger than maximum number of pixels ({nmax_pixels}).')
            print('Reduce size of bounding box or set target resolution to larger value.')
            return False
    return True


def check_target_sources(target_sources):
    """
    Validate selected data layers and options

    TBD: GEE validations
    """

    for source in list(target_sources.keys()):
        # Check DEA
        if source == 'DEA':
            layers = target_sources[source]
            dict_dea = get_deadict()
            options = list(dict_dea["layernames"].keys())
            # Check that all elements in source are a subset of dea
            ok = set(layers).issubset(set(options))
            if not ok:
                for layer in layers:
                    if layer not in options:
                        print(f'Datalayer "{layer}" not supported for {source}.')
                        print('Supported data layers are: ',  options)
                return False
        
        # Check DEM
        if source == 'DEM':
            layers = target_sources[source]
            dict_dem = get_demdict()
            options = list(dict_dem["layernames"].keys())
            # Check that all elements in source are a subset
            ok = set(layers).issubset(set(options))
            if not ok:
                for layer in layers:
                    if layer not in options:
                        print(f'Datalayer "{layer}" not supported for {source}.')
                        print('Supported data layers are: ',  options)
                return False

        # Check Landscape
        if source == 'Landscape':
            layers = target_sources[source]
            dict_landscape = get_landscapedict()
            options = list(dict_landscape["layernames"].keys())
            # Check that all elements in source are a subset
            ok = set(layers).issubset(set(options))
            if not ok:
                for layer in layers:
                    if layer not in options:
                        print(f'Datalayer "{layer}" not supported for {source}.')
                        print('Supported data layers are: ',  options)
                return False

        # Check Radiometric
        if source == 'Radiometric':
            layers = target_sources[source]
            dict_radiometric = get_radiometricdict()
            options = list(dict_radiometric["layernames"].keys())
            # Check that all elements in source are a subset
            ok = set(layers).issubset(set(options))
            if not ok:
                for layer in layers:
                    if layer not in options:
                        print(f'Datalayer "{layer}" not supported for {source}.')
                        print('Supported data layers are: ',  options)
                return False

        # Check SLGA
        if source == 'SLGA':
            layers = target_sources[source]
            depth_options = ['0-5cm','5-15cm','15-30cm','30-60cm','60-100cm','100-200cm']
            dict_slga = get_slgadict()
            options = list(dict_slga["layers_url"].keys())
            # Check that all elements in source are a subset
            ok = set(layers).issubset(set(options))
            if not ok:
                for layer in list(layers.keys()):
                    if layer not in options:
                        print(f'Datalayer "{layer}" not supported for {source}.')
                        print('Supported data layers are: ',  options)
                return False
            # check if valid depth selected:
            for layer in list(layers.keys()):
                depths = layers[layer]
                ok = set(depths).issubset(set(depth_options))
                if not ok:
                    for depth in depths:
                        if depth not in depth_options:
                            print(f'Depth "{depth}" not supported as SLGA depth option.')
                            print('Supported depths are: ',  depth_options)
                    return False

        # Check SILO
        if source == 'SILO':
            layers = target_sources[source]
            silo_options = ['mean', 'median', 'sum', 'std', 'perc95', 'perc5', 'max', 'min']
            dict_silo = get_silodict()
            options = list(dict_silo["layernames"].keys())
            # Check that all elements in source are a subset
            ok = set(layers).issubset(set(options))
            if not ok:
                for layer in list(layers.keys()):
                    if layer not in options:
                        print(f'Datalayer "{layer}" not supported for {source}.')
                        print('Supported data layers are: ',  options)
                return False
            # check if valid aggregation options selected:
            for layer in list(layers.keys()):
                agoptions = layers[layer]
                ok = set(agoptions).issubset(set(silo_options))
                if not ok:
                    for agoption in agoptions:
                        if agoption not in silo_options:
                            print(f'Option "{agoption}" not supported as temporal SILO aggregation option.')
                            print('Supported options are: ',  silo_options)
                    return False

        # Check GEE: TBD!
        #if source == 'GEE':
        #   ...

    return True


def validate(fname_settings, verbose=False):
    """
    Validates all settings with regard
        - schema
        - date range
        - data size and bounding box
        - data layers and options

    INPUT:
    fname_settings: str, path + filename of settings
    """
    #fname_settings = 'settings/settings_v0.3.yaml'

    # Logger setup
    if verbose:
        write_logs.setup(level="info")
    else:
        write_logs.setup()

    with open(fname_settings, 'r') as f:
        settings = yaml.load(f, Loader=yaml.FullLoader)

    # Check that schema is ok
    schema_ok = check_schema(settings)
    assert schema_ok, "Invalid Schema"
    
    # Check requested image size
    # Note that this is an upper limit and does not ensure Webservers reaches timeout
    bbox = settings['target_bbox']
    target_res = settings['target_res']
    size_ok = check_target_size(bbox, target_res)
    assert size_ok, "Invalid Size"

    # Check if requested dates are in valid range
    dates = settings['target_dates']
    dates_ok = check_target_dates(dates)
    assert dates_ok, "Invalid Dates"

    # Check if data layers and options ok
    target_sources = settings['target_sources']
    targets_ok = check_target_sources(target_sources)
    assert targets_ok, "Invalid Data layers or options"

    logging.print(f"✓ | Validation of settings file ok")
