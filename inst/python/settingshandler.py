# Settings Reader

import yaml
import urllib
import json
from types import SimpleNamespace

# Defaul settings yaml file
_fname_settings = "settings/settings_v0.1_default.yaml"


def main(fname_settings=_fname_settings, to_namespace=True):
    """
    Main function for running the script.

    Input:
        fname_settings: path and filename to settings file
    """
    # Load settings from yaml file
    with open(fname_settings, "r") as f:
        settings = yaml.load(f, Loader=yaml.FullLoader)
    # Parse settings dictinary as namespace (settings are available as
    # settings.variable_name rather than settings['variable_name'])
    if to_namespace:
        settings = SimpleNamespace(**settings)

    return settings


def ee_stac():
    """
    Returns full list of STAC IDs from the Earth Engine Data Catalog
    """
    try:
        stac_url = "https://raw.githubusercontent.com/samapriya/Earth-Engine-Datasets-List/master/gee_catalog.json"
        datasets = []
        with urllib.request.urlopen(stac_url) as url:
            data = json.loads(url.read().decode())
            datasets = [item["id"] for item in data]
        return datasets
    except Exception as e:
        raise Exception(e)
