"""
This script generates interactive notebook widgets for selecting the settings.

Widgets are defined using the package ipywidgets, for more details see:

https://ipywidgets.readthedocs.io/en/stable/index.html

and examples:
https://coderzcolumn.com/tutorials/python/interactive-widgets-in-jupyter-notebook-using-ipywidgets


This package is part of the Data Harvester project developed for the Agricultural Research Federation (AgReFed).

Copyright 2022 Sydney Informatics Hub (SIH), The University of Sydney

This open-source software is released under the LGPL-3.0 License.

TBD:
- convert bbox string to list of floats
settings.target_bbox = settings.target_bbox.strip('][').split(', ')
settings.target_bbox = [float(item) for item in settings.target_bbox]

"""

import os
import yaml
import sys
import ipywidgets as widgets
from IPython.display import display
import datetime
from types import SimpleNamespace

# import data dictionaries
sys.path.append("../")
from .ipyfilechooser import FileChooser
from getdata_slga import get_slgadict
from getdata_silo import get_silodict
from getdata_dea import get_deadict
from getdata_radiometric import get_radiometricdict
from getdata_landscape import get_landscapedict


def gen_accordion(panels, panel_titles):
    # Generate accordion of panels
    accordion_main = widgets.Accordion(children=panels)
    # in future version its is possible to use title attribute in accordion
    # titles=[io_title, st_title, slga_title, silo_title, dea_title, dem_title]
    for i in range(len(accordion_main.children)):
        accordion_main.set_title(i, panel_titles[i])
    return accordion_main


def save_dict_settings(dict_settings, yaml_outfname):
    """
    save dictionary to yaml file
    """
    # save dictionary to yaml file
    f = open(yaml_outfname, "w+")
    yaml.dump(dict_settings, f, allow_unicode=True, default_flow_style=False)
    print(f"Settings saved to file {yaml_outfname}")


def load_settings(fname_settings):
    """
    Input:
        fname_settings: path and filename to settings file
    """
    # Load settings from yaml file
    with open(fname_settings, "r") as f:
        settings = yaml.load(f, Loader=yaml.FullLoader)
    # Parse settings dictinary as namespace (settings are available as
    # settings.variable_name rather than settings['variable_name'])
    settings = SimpleNamespace(**settings)
    return settings


def gen_loadwidget():
    w_yamlfile = FileChooser(os.getcwd(), title="Settings File:")
    return w_yamlfile


def gen_maintab():
    """Generate New Settings Tab"""
    w_load = gen_loadwidget()
    # panels, w_settings, w_names, w_save = gen_widgets()
    panels, w_settings, names_settings, panel_titles = gen_panels()
    accordion = gen_accordion(panels, panel_titles)
    # w_save = gen_savebutton()
    # w_new = widgets.VBox([accordion, w_save])
    w_new = accordion
    tab_nest = widgets.Tab()
    tab_nest.children = [w_new, w_load]
    tab_titles = ["New Settings", "Load Settings"]
    for i in range(len(tab_nest.children)):
        tab_nest.set_title(i, tab_titles[i])
    return tab_nest, w_settings, names_settings, w_load


def gen_savebutton():
    """Generate Save button"""
    w_savebutton = widgets.ToggleButton(
        description="Save Settings",
        # button_style='', # 'success', 'info', 'warning', 'danger' or ''
        # tooltip='Click me',
        # icon='check'
    )
    return w_savebutton


def savebutton_onclick(params):
    # functionality with non-name params not supported yet by widgets
    w_settings, name_settings, yaml_outfname = params
    save_dict_settings(eval_widgets(w_settings, names_settings), yaml_outfname)
    print(f"Settings saved to file {yaml_outfname}")


def gen_panel_io():
    # Generate I/O panel
    w_inpath = FileChooser(os.getcwd(), title="Input File:")

    # Write name relative output path
    w_outpath = widgets.Text(
        value="../../dataresults/",
        placeholder="Type name of output path",
        description="Output Path:",
        disabled=False,
    )

    # Write name of longitude
    w_colname_lng = widgets.Text(
        value="",
        placeholder="Type name of Longitude column",
        description="",
        disabled=False,
    )

    # Write name of latitude
    w_colname_lat = widgets.Text(
        value="",
        placeholder="Type name of Latitude column",
        description="",
        disabled=False,
    )

    # box1_io = widgets.HBox([w_inpath, w_outpath])
    # box2_io = widgets.HBox([
    #    widgets.Box([widgets.Label("Headername of Longitude:"), w_colname_lng]),
    #     widgets.Box([widgets.Label("Headername of Longitude:"), w_colname_lng])
    #    ])

    items = [
        w_inpath,
        widgets.Box([widgets.Label("Headername of Longitude:"), w_colname_lng]),
        w_outpath,
        widgets.Box([widgets.Label("Headername of Latitude:"), w_colname_lat]),
    ]

    panel_io = widgets.GridBox(
        items, layout=widgets.Layout(grid_template_columns="2fr 3fr")
    )
    # widgets.VBox([w_inpath, w_outpath, box2_io])

    w_io = [w_inpath, w_outpath, w_colname_lng, w_colname_lat]
    w_names = ["infile", "outpath", "colname_lng", "colname_lat"]
    return panel_io, w_io, w_names


def gen_panel_st():
    # spatial-temporal specs

    w_target_bbox = widgets.Text(
        value="",
        placeholder="[left, bottom, right, top]",
        description="",
        disabled=False,
    )

    w_target_res = widgets.FloatSlider(
        value=3,
        min=0.3,
        max=100,
        step=0.1,
        description="",
        disabled=False,
        continuous_update=False,
        orientation="horizontal",
        readout=True,
        slider_color="white",
    )

    currentDateTime = datetime.datetime.now()
    current_year = currentDateTime.date().year
    date_options = [*range(1970, current_year + 1, 1)]
    date_options.reverse()

    w_target_dates = widgets.SelectMultiple(
        options=date_options,
        value=[current_year - 1],
        rows=3,
        description="",
        disabled=False,
    )

    w_temp_res = widgets.IntSlider(
        value=30,
        min=1,
        max=365,
        step=1,
        description="",
        disabled=False,
        continuous_update=False,
        orientation="horizontal",
        readout=True,
        slider_color="white",
    )

    items = [
        widgets.Box([widgets.Label("Bounding Box:"), w_target_bbox]),
        widgets.Box([widgets.Label("Spatial Resolution [arcsec]:"), w_target_res]),
        widgets.Box([widgets.Label("Select years:"), w_target_dates]),
        widgets.Box([widgets.Label("Temporal Resolution [days]:"), w_temp_res]),
    ]

    # settings_st = [w_target_bbox, w_target_res, w_target_date_min, w_target_date_max, w_temp_res]
    # settings_names = ['target_bbox', 'target_res', 'target_date_min', 'target_date_max', 'temp_res']
    settings_st = [w_target_bbox, w_target_res, w_target_dates, w_temp_res]
    settings_names = ["target_bbox", "target_res", "target_dates", "temp_res"]
    panel_st = widgets.GridBox(
        items, layout=widgets.Layout(grid_template_columns="3fr 3fr")
    )
    return panel_st, settings_st, settings_names


def gen_panel_slga():
    # Generate SLGA panel
    ## SLGA
    dict_slga = get_slgadict()
    options_slga = list(dict_slga["layers_url"].keys())

    w_slga = []
    box_slga = []
    for option in options_slga:
        w_sel = widgets.Checkbox(
            value=False, description=option, disabled=False, indent=False
        )
        w_depth = widgets.SelectMultiple(
            options=["0-5cm", "5-15cm", "15-30cm", "30-60cm", "60-100cm", "100-200cm"],
            value=["0-5cm"],
            rows=2,
            description="Depths:",
            disabled=False,
        )

        w_slga.append([w_sel, w_depth])
        box = widgets.HBox([w_sel, w_depth])
        box_slga.append(box)

    panel_slga = widgets.VBox(box_slga)
    return panel_slga, w_slga, options_slga


def gen_panel_silo():
    # Generate SILO panel
    ## SILO
    dict_silo = get_silodict()
    options_silo = list(dict_silo["layernames"].keys())
    desc_silo = list(dict_silo["layernames"].values())

    w_silo = []
    box_silo = []
    for i in range(len(options_silo)):
        option = options_silo[i]
        desc = desc_silo[i]
        w_sel = widgets.Checkbox(
            value=False, description=option, disabled=False, indent=False
        )
        w_temp = widgets.SelectMultiple(
            # options=['Total','Median','Mean','Std','5pct','10pct','15pct','25pct','75pct','85pct','90pct','95pct'],
            options=["mean", "median", "sum", "std", "perc95", "perc5", "max", "min"],
            value=["median"],
            rows=2,
            description="",
            disabled=False,
        )
        w_silo.append([w_sel, w_temp])
        items = [
            w_sel,
            widgets.Box([widgets.Label("Temporal Stats: "), w_temp]),
            widgets.Label(desc),
        ]
        box = widgets.GridBox(
            items, layout=widgets.Layout(grid_template_columns="1fr 2fr 3fr")
        )
        # box = widgets.HBox([w_sel, widgets.Box([widgets.Label("Temporal Stats: "), w_temp]), widgets.Label(desc)])
        box_silo.append(box)

    panel_silo = widgets.VBox(box_silo)
    return panel_silo, w_silo, options_silo


def gen_panel_dea():
    # Generate DEA panel
    ## DEA
    dict_dea = get_deadict()
    options_dea = list(dict_dea["layernames"].keys())
    desc_dea = list(dict_dea["layernames"].values())

    w_dea = []
    box_dea = []
    for i in range(len(options_dea)):
        option = options_dea[i]
        desc = desc_dea[i]
        w_sel = widgets.Checkbox(
            value=False, description=option, disabled=False, indent=False
        )
        # If any temporal aggregation needed, uncomment following lines
        # w_temp = widgets.SelectMultiple(
        # value=['Median'],
        # rows=2,
        # description='',
        # disabled=False
        # )
        # w_dea.append([w_sel, w_temp])
        # items = [w_sel, widgets.Box([widgets.Label("Temporal Stats: "), w_temp]), widgets.Label(desc)]
        # box = widgets.GridBox(items, layout=widgets.Layout(grid_template_columns="1fr 2fr 3fr"))
        w_dea.append([w_sel])
        items = [w_sel, widgets.Label(desc)]
        box = widgets.GridBox(
            items, layout=widgets.Layout(grid_template_columns="1fr 3fr")
        )
        # box = widgets.HBox([w_sel, widgets.Box([widgets.Label("Temporal Stats: "), w_temp]), widgets.Label(desc)])
        box_dea.append(box)
    panel_dea = widgets.VBox(box_dea)
    return panel_dea, w_dea, options_dea


def gen_panel_dem():
    # generate DEM panel
    ## DEM
    options_dem = ["DEM", "Slope", "Aspect"]
    desc_dem = [
        "Digital Elevation Model (DEM) of Australia derived from STRM with 1 Second Grid - Hydrologically Enforced.",
        "DEM Slope",
        "DEM Aspect Ratio",
    ]
    w_dem = []
    box_dem = []
    for i in range(len(options_dem)):
        option = options_dem[i]
        desc = desc_dem[i]
        w_sel = widgets.Checkbox(
            value=False, description=option, disabled=False, indent=False
        )
        w_dem.append([w_sel])
        items = [w_sel, widgets.Label(desc)]
        box = widgets.GridBox(
            items, layout=widgets.Layout(grid_template_columns="1fr 4fr")
        )
        # box = widgets.HBox([w_sel, widgets.Box([widgets.Label("Temporal Stats: "), w_temp]), widgets.Label(desc)])
        box_dem.append(box)

    panel_dem = widgets.VBox(box_dem)
    return panel_dem, w_dem, options_dem


def gen_panel_radiometric():
    # Generate radiometrics panel
    dict_rm = get_radiometricdict()
    desc_rm = list(dict_rm["layernames"].values())
    options_rm = list(dict_rm["layernames"].keys())

    w_rm = []
    box_rm = []
    for i in range(len(options_rm)):
        option = options_rm[i]
        desc = desc_rm[i]
        w_sel = widgets.Checkbox(
            value=False, description=option, disabled=False, indent=False
        )
        w_rm.append([w_sel])
        items = [w_sel, widgets.Label(desc)]
        box = widgets.GridBox(
            items, layout=widgets.Layout(grid_template_columns="2fr 3fr")
        )
        box_rm.append(box)
    panel_rm = widgets.VBox(box_rm)
    return panel_rm, w_rm, options_rm


def gen_panel_landscape():
    # Generate radiometrics panel
    dict_ls = get_landscapedict()
    options_ls = list(dict_ls["layernames"].keys())
    w_ls = []
    box_ls = []
    for i in range(len(options_ls)):
        option = options_ls[i]
        w_sel = widgets.Checkbox(
            value=False, description=option, disabled=False, indent=False
        )
        w_ls.append([w_sel])
        items = [w_sel]
        box = widgets.GridBox(items, layout=widgets.Layout(grid_template_columns="1fr"))
        box_ls.append(box)
    panel_ls = widgets.VBox(box_ls)
    return panel_ls, w_ls, options_ls


def gen_panels():
    # Generate New Settings panels

    panel_io, w_io, names_io = gen_panel_io()

    panel_st, w_st, names_st = gen_panel_st()

    panel_slga, w_slga, names_slga = gen_panel_slga()

    panel_silo, w_silo, names_silo = gen_panel_silo()

    panel_dea, w_dea, names_dea = gen_panel_dea()

    panel_dem, w_dem, names_dem = gen_panel_dem()

    panel_rm, w_rm, names_rm = gen_panel_radiometric()

    panel_ls, w_ls, names_ls = gen_panel_landscape()

    ## define return objects
    w_settings = [
        w_io,
        w_st,
        w_slga,
        w_silo,
        w_dea,
        w_dem,
        w_rm,
        w_ls,
    ]

    panels = [
        panel_io,
        panel_st,
        panel_slga,
        panel_silo,
        panel_dea,
        panel_dem,
        panel_rm,
        panel_ls,
    ]

    names_settings = [
        names_io,
        names_st,
        names_slga,
        names_silo,
        names_dea,
        names_dem,
        names_rm,
        names_ls,
    ]

    io_title = "Input and Output Specifications"
    st_title = "Settings for Spatial and Temporal Specifications"
    slga_title = "SLGA Data Selection"
    silo_title = "SILO Data Selection"
    dea_title = "DEA Data Selection"
    dem_title = "DEM Data Selection"
    rm_title = "Radiometrics Data Selection"
    ls_title = "Landscape Data Selection"

    panel_titles = [
        io_title,
        st_title,
        slga_title,
        silo_title,
        dea_title,
        dem_title,
        rm_title,
        ls_title,
    ]

    return panels, w_settings, names_settings, panel_titles


def eval_widgets(w_settings, names):
    """
    This function is converting widget settings into dictionary.

    If widget settings change, add settings here too.
    """
    w_io, w_st, w_slga, w_silo, w_dea, w_dem, w_rm, w_ls = w_settings
    (
        names_io,
        names_st,
        names_slga,
        names_silo,
        names_dea,
        names_dem,
        names_rm,
        names_ls,
    ) = names

    dict_settings = {}
    # I/O
    assert len(names_io) == len(w_io)
    for i in range(len(w_io)):
        dict_settings[names_io[i]] = w_io[i].value
    # ST settings
    assert len(names_st) == len(w_st)
    for i in range(len(w_st)):
        dict_settings[names_st[i]] = w_st[i].value
    # target sources settings
    # define for target source a dictionary
    # Loop over all settings and add the ones that are selected
    dict_sources = {}
    # SLGA
    slist = {}
    for i in range(len(w_slga)):
        if w_slga[i][0].value:
            slist[names_slga[i]] = list(w_slga[i][1].value)
    dict_sources["SLGA"] = slist
    # SILO
    slist = {}
    for i in range(len(w_silo)):
        if w_silo[i][0].value:
            slist[names_silo[i]] = list(w_silo[i][1].value)
    dict_sources["SILO"] = slist
    # DEA
    slist = []
    for i in range(len(w_dea)):
        if w_dea[i][0].value:
            # slist.append({names_dea[i]: list(w_dea[i][1].value)})
            slist.append(names_dea[i])
    dict_sources["DEA"] = slist
    # DEM
    slist = []
    for i in range(len(w_dem)):
        if w_dem[i][0].value:
            slist.append(names_dem[i])
    dict_sources["DEM"] = slist
    # Radiometric
    slist = []
    for i in range(len(w_rm)):
        if w_rm[i][0].value:
            slist.append(names_rm[i])
    dict_sources["Radiometric"] = slist
    slist = []
    # Landscape
    for i in range(len(w_ls)):
        if w_ls[i][0].value:
            slist.append(names_ls[i])
    dict_sources["Landscape"] = slist
    # Add here any new settings or data sources
    dict_settings["target_sources"] = dict_sources
    return dict_settings


def print_settings(settings):
    """
    print settings
    """
    print("Settings loaded:")
    print("----------------")
    for key in settings.__dict__:
        if key == "target_sources":
            print(f"settings.{key}:")
            for source in settings.target_sources:
                print(f"   '{source}': {settings.target_sources[source]}")
        else:
            print(f"settings.{key} : {settings.__dict__[key]}")
