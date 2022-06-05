# Settings Reader

import yaml
import os
from types import SimpleNamespace  

# Defaul settings yaml file
_fname_settings = 'settings/settings_v0.1_default.yaml'


def main(fname_settings = _fname_settings):
    """
    Main function for running the script.

    Input:
        fname_settings: path and filename to settings file
    """
    # Load settings from yaml file
    with open(fname_settings, 'r') as f:
        settings = yaml.load(f, Loader=yaml.FullLoader)
    # Parse settings dictinary as namespace (settings are available as 
    # settings.variable_name rather than settings['variable_name'])
    settings = SimpleNamespace(**settings)

    return settings