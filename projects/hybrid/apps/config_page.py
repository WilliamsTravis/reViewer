# -*- coding: utf-8 -*-
"""Configuration Application.

Created on Sun Aug 23 16:27:25 2020

@author: travis
"""
import ast
import csv
import json
import os

from glob import glob

import dash
import dash_core_components as dcc
import dash_html_components as html
import numpy as np
import pandas as pd
import tkinter as tk

from dash_table import DataTable
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
from review.support import CONFIG_PATH, ORIGINAL_FIELDS, TITLES, UNITS
from review.support import get_scales, Config

from app import app
from review import print_args
from tkinter import filedialog

# MAC Tkinter solution?
import matplotlib
# matplotlib.use("TkAgg")


PROJECTS = [{"label": p, "value": p} for p in Config().projects]


layout = html.Div([
    # Start of the page
    html.H3("Configure Project"),

    # Project name
    html.H5("Project Name"),
    html.Div([
        html.Div([
            html.H6("Create New Project:"),
            dcc.Input(
                id="project_name",
                debounce=True,
                placeholder="Enter project name",
                style={"width": "100%", "margin-left": "26px"}
            )
        ]),
        html.Div([
            html.H6("Edit Existing Project:"),
            dcc.Dropdown(
                id="project_list",
                options=PROJECTS,
                placeholder="Select project name",
                style={"width": "100%", "margin-left": "15px"}
            )
        ]),
        ],
        style={"margin-left": "50px", "margin-bottom": "15px", "width": "35%"},
        className="row"
    ),

    # Project directory
    html.H5("Find Project Directory", style={"margin-top": "50px"}),
    html.Div([
        html.Button(
            children="navigate",
            title="Navigate the file system for the project directory.",
            id="proj_nav",
            n_clicks=0
        ),
        dcc.Input(
            id="proj_input",
            placeholder="/",
            name="name_test",
            debounce=True,
            style={"width": "36%"}
        ),
    ], className="row",
       style={"margin-left": "50px"}
    ),
    html.Div(
        id="project_directory_print"
    ),

    # Create Group
    html.H5("Create Groups", style={"margin-top": "50px"}),
    html.Div([
        html.Button(
            children="Add Group",
            id="submit_group"
        ),
        dcc.Input(
            id="group_input",
            placeholder="Input group name."
        ),
        dcc.Input(
            id="group_value_input",
            placeholder="Input possible values.",
            style={"width": "27.5%"}
        ),
    ], className="row",
        style={"margin-left": "50px", "margin-bottom": "15px"}
    ),

    html.Div(id="top_groups",
             style={"margin-bottom": "50px", "width": "50%"}),

    # Dataset paths
    html.H5("Add Data Set(s)", style={"margin-top": "50px"}),
    html.Div([
        html.Button(
            id="file_nav",
            children="navigate",
            title=("Navigate the file system for a reV supply curve data "
                   "set."),
            n_clicks=0
        ),
        dcc.Input(
            id="file_pattern",
            debounce=True,
            placeholder="Glob Pattern",
            style={"width": "36%"}
        ),
        html.Div(
            id="file_groups",
            style={"margin-bottom": "50px", "width": "50%"}
        ),
    ], className="row",
        style={"margin-left": "50px", "margin-bottom": "15px"}),

    # Add extra field entries
    html.H5("New Fields Detected"),
    html.Div(
        id="extra_fields",
        style={"margin-left": "50px", "margin-bottom": "50px",
               "width": "50%"}
    ),

    # Submit and trigger configuration build/update
    html.Button(
        id="submit",
        children="submit",
        title="Submit above values and build the project configuration file.",
        n_clicks=0
    ),

    # Storage
    html.Div(id="proj_dir", style={"display": "none"}, children="/"),
    html.Div(id="groups", children="{}", style={"display": "none"}),
    html.Div(id="files", children="{}", style={"display": "none"}),
    html.Div(id="config", style={"display": "none"})

], className="twelve columns", style={"margin-bottom": "50px"})


def dash_to_pandas(dt):
    """Convert a dash data table to a pandas data frame."""
    df = pd.DataFrame(dt["props"]["data"])
    try:
        df = df.apply(lambda x: ast.literal_eval(x), axis=0)
        msg = "File attributes read successfully."
    except ValueError:
        msg = "File attributes contain missing values."
    return df, msg


def navigate(which, initialdir="/"):
    """Browse directory for file or folder paths."""
    # Print variables
    print_args(navigate, which, initialdir)

    filetypes = [('ALL', '*'), ('CSV', '*.csv')]

    root = tk.Tk()
    root.withdraw()
    root.geometry("1000x200")
    root.resizable(0, 0)
    back = tk.Frame(master=root, bg='black')
    back.pack_propagate(0)

    root.option_add('*foreground', 'black')
    root.option_add('*activeForeground', 'black')
    # root.option_add('*font', 'arial')

    # style = ttk.Style(root)
    # style.configure('TLabel', foreground='black', font=font)
    # style.configure('TEntry', foreground='black', font=font)
    # style.configure('TMenubutton', foreground='black', font=font)
    # style.configure('TButton', foreground='black', font=font)

    if which == "files":
        paths = filedialog.askopenfilenames(master=root, filetypes=filetypes,
                                            initialdir=initialdir)
    else:
        paths = filedialog.askdirectory(master=root)

    root.destroy()

    return paths


@app.callback(Output("project_list", "options"),
              [Input("project_name", "value")])
def project_list(name):
    """Return or update & return available project list."""
    projects = Config().projects
    if name:
        if name not in projects:
            projects = projects + [name]
    projects = [{"label": p, "value": p} for p in projects]
    return projects


@app.callback(Output("project_name", "value"),
              [Input("project_list", "value")])
def project_name(selection):
    """Add an existing project selection to the project name entry."""
    return selection


@app.callback([Output("proj_input", "placeholder"),
               Output("proj_dir", "children"),
               Output("project_directory_print", "children")],
              [Input("project_name", "value"),
               Input("proj_nav", "n_clicks"),
               Input("proj_input", "value")])
def find_project_directory(name, n_clicks, path):
    """Find the root project directory containing data files."""
    # Print variables
    trig = dash.callback_context.triggered[0]['prop_id']
    print_args(find_project_directory, name, n_clicks, path, trig=trig)

    if name in Config().projects:
        config = Config(name)
        path = config.directory

    if "proj_nav" in trig:
        if n_clicks > 0:
            path = navigate("folders")

    if path:
        if not os.path.exists(path):
            print("Chosen path does not exist.")
    else:
        path = "/"

    sdiv = html.Div(
            id="project_directory",
            children=[
                html.P(path),
            ],
            className="row",
            style={"margin-left": "100px", "margin-bottom": "15px"}
        )

    return path, path, sdiv


@app.callback([Output("top_groups", "children"),
               Output("groups", "children")],
              [Input("submit_group", "n_clicks"),
               Input("project_name", "value")],
              [State("group_input", "value"),
               State("group_value_input", "value"),
               State("groups", "children")])
def create_groups(submit, name, group_input, group_values, group_dict):
    """Set a group with which to categorize datasets."""
    print_args(create_groups, submit, name, group_input, group_values,
               group_dict)

    group_dict = json.loads(group_dict)

    if name in Config().projects:
        config = Config(name)
        data = config.data
        groups = [c for c in data.columns if c not in ["name", "file"]]
        groups = {g: ", ".join(data[g].unique()) for g in groups}
    else:
        if name in group_dict:
            groups = group_dict[name]
        else:
            groups = {}

    if group_input:
        groups[group_input] = group_values


    df = pd.DataFrame(groups, index=[0]).T
    df = df.reset_index()
    df.columns = ["group", "values"]

    dt = DataTable(
            id="group_table",
            data=df.to_dict("records"),
            columns=df.columns,
            editable=True,
            column_selectable="multi",
            row_deletable=True,
            row_selectable="multi",
            page_size=10,
            style_cell={"textAlign": "left"},
            style_data_conditional=[
                {
                    "if": {"row_index": "odd"},
                    "backgroundColor": "rgb(232,240,254)"
                }
            ],
            style_header={
                "backgroundColor": "rgb(22,99,181)",
                "color": "rgb(255,255,255)",
                "fontWeight": "bold"
            }
        )

    dt = []
    for group, values in groups.items():
        if group:
            reminder = "**{}**: {}".format(group, values)
            sdiv = dcc.Markdown(
                    id="{}_options".format(group),
                    children=reminder,
                    className="row",
                    style={"margin-left": "100px", "margin-bottom": "15px"}
                )
            dt.append(sdiv)

    group_dict[name] = groups
    group_dict = json.dumps(group_dict)

    # print(dt)

    return dt, group_dict


@app.callback(Output("files", "children"),
              [Input("file_nav", "n_clicks"),
               Input("file_pattern", "value"),
               Input("project_name", "value")],
              [State("proj_dir", "children"),
               State("files", "children")])
def add_datasets(n_clicks, pattern, name, initialdir, file_dict):
    """Browse the file system for a list of file paths."""
    trig = dash.callback_context.triggered[0]['prop_id']
    print_args(add_datasets, n_clicks, pattern, name, initialdir, file_dict,
                trig=trig)

    file_dict = json.loads(file_dict)

    if file_dict == {} or file_dict is None or name not in file_dict:
        files = []
    elif name in file_dict:
        files = file_dict[name]

    if name in Config().projects:
        config = Config(name)
        files = config.data
        pdir = config.directory
        files["path"] = files["file"].apply(lambda x: os.path.join(pdir, x))
        files = list(files["path"].values)

    if "file_nav" in trig:
        if n_clicks > 0:
            paths = navigate("files", initialdir=initialdir)
            for path in paths:
                if not os.path.exists(path):
                    raise OSError(path + "does not exist.")
                files.append(os.path.join(initialdir, path))

    elif "file_pattern" in trig:
        new_files = glob(os.path.join(initialdir, pattern), recursive=True)
        new_files.sort()
        files = files + new_files

    elif "project_name" not in trig:
        raise PreventUpdate

    files = [file for file in files if os.path.exists(file)]
    file_dict[name] = files
    file_dict = json.dumps(file_dict)

    return file_dict


@app.callback(Output("file_groups", "children"),
              [Input("files", "children"),
               Input("proj_dir", "children"),
               Input("groups", "children")],
              [State("project_name", "value")])
def set_dataset_groups(file_dict, proj_dir, group_dict, name):
    """For each file, set a group and value from the user inputs above."""
    print_args(set_dataset_groups, file_dict, proj_dir, group_dict, name)
    file_dict = json.loads(file_dict)

    if not name:
        return None

    if name not in file_dict:
        raise PreventUpdate

    if not file_dict[name]:
        return None

    if "null" in file_dict:
        del file_dict["null"]

    if file_dict and name in file_dict:
        files = file_dict[name]
        try:
            groups = json.loads(group_dict)[name]
        except Exception as e:
            print(e)
            raise PreventUpdate
        groups = {k: v.split(",") for k, v in groups.items()}
        groups = {k: [v.split()[0] for v in g] for k, g in groups.items()}
        groups = {k: v + ["NA"] for k, v in groups.items()}

        # Dropdowns
        dropdowns = {}
        for group, options in groups.items():
            options = [{"label": op, "value": op} for op in options]
            dropdowns[group] = {
                "options": options,
            }

        # Data Table
        if name in Config().projects:
            config = Config(name)
            df = config.data
            if "name" in df:
                del df["name"]
            pdir = config.directory
            df["file"] = df["file"].apply(lambda x: os.path.join(pdir, x))
            new_rows = []
            for file in files:
                if file not in df["file"].values:
                    row = df.iloc[0]
                    for key in row.keys():
                        row[key] = None
                    row["file"] = file
                    new_rows.append(row)
            if new_rows:
                ndf = pd.DataFrame(new_rows)
                df = pd.concat([df, ndf])
            df = df.reset_index(drop=True)
        else:
            df = pd.DataFrame({"file": files})
            for group, options in groups.items():
                df[group] = ", ".join(options)

        cols = []
        for col in df.columns:
            if col in groups.keys():
                entry = {"name": col, "id": col, "presentation": "dropdown"}
            else:
                entry = {"name": col, "id": col, "searchable": True}
            cols.append(entry)

        dt = DataTable(
                id="group_table",
                data=df.to_dict("records"),
                columns=cols,
                editable=True,
                column_selectable="multi",
                row_deletable=True,
                row_selectable="multi",
                page_size=10,
                dropdown=dropdowns,
                style_cell={"textAlign": "left"},
                style_data_conditional=[
                    {
                        "if": {"row_index": "odd"},
                        "backgroundColor": "rgb(232,240,254)"
                    }
                ],
                style_header={
                    "backgroundColor": "rgb(22,99,181)",
                    "color": "rgb(255,255,255)",
                    "fontWeight": "bold"
                }
            )

        return dt


@app.callback(Output("extra_fields", "children"),
              [Input("files", "children"),
               Input("groups", "children")],
              [State("extra_fields", "children"),
               State("project_name", "value")])
def find_extra_fields(file_dict, group_dict, fields, name):
    """Use one of the files to infer extra fields and assign units."""
    print_args(find_extra_fields, file_dict, group_dict, fields, name)

    group_dict = json.loads(group_dict)
    file_dict = json.loads(file_dict)

    if not name:
        raise PreventUpdate

    if name not in file_dict:
        raise PreventUpdate

    if not file_dict[name]:
        return None

    if "null" in file_dict:
        del file_dict["null"]

    if not file_dict:
        raise PreventUpdate
    if not group_dict:
        raise PreventUpdate

    files = file_dict[name]
    groups = group_dict[name]

    new_fields = []
    if files:
        for file in files:
            if os.path.isfile(file):
                with open(file, "r") as f1:
                    reader = csv.DictReader(f1)
                    columns = reader.fieldnames
                new_columns = list(set(columns) - set(ORIGINAL_FIELDS))
                new_fields = new_fields + new_columns
        new_fields = list(np.unique(new_fields))
    else:
        raise PreventUpdate

    new_fields = new_fields + list(groups.keys())

    df = pd.DataFrame(new_fields)
    df["title"] = "N/A"
    df["units"] = "N/A"
    df.columns = ["FIELD", "TITLE", "UNITS"]

    if name in Config().projects:
        config = Config(name)
        for field, title in config.titles.items():
            df["TITLE"][df["FIELD"] == field] = title
        for field, unit in config.units.items():
            df["UNITS"][df["FIELD"] == field] = unit

    cols = [{"name": i, "id": i, "searchable": True} for i in df.columns]
    cell_styles = [
        {"if": {"column_id": "UNITS"}, "width": "45px"},
        {"if": {"column_id": "FIELD"}, "width": "75px"},
        {"if": {"column_id": "TITLE"}, "width": "75px"}
    ]

    dt = DataTable(
            id="field_table",
            data=df.to_dict("records"),
            columns=cols,
            editable=True,
            column_selectable="multi",
            row_selectable="multi",
            row_deletable=True,
            page_size=10,
            style_cell={"textAlign": "left"},
            style_cell_conditional=cell_styles,
            style_data_conditional=[
                {
                    "if": {"row_index": "odd"},
                    "backgroundColor": "rgb(232,240,254)"
                }
            ],
            style_header={
                "backgroundColor": "rgb(22,99,181)",
                "color": "rgb(255,255,255)",
                "fontWeight": "bold"
            }
        )

    return dt


@app.callback(Output("config", "children"),
              [Input("submit", "n_clicks")],
              [State("file_groups", "children"),
               State("project_name", "value"),
               State("proj_dir", "children"),
               State("extra_fields", "children")])
def build_config(n_clicks, group_dt, name, directory, fields):
    """Consolidate inputs into a project config and update overall config."""
    print_args(build_config, n_clicks, group_dt, name, directory,
               fields)

    if n_clicks == 0:
        raise PreventUpdate

    # Get the file/group and fields data frames
    field_df, fmsg = dash_to_pandas(fields)
    file_df, gmsg = dash_to_pandas(group_dt)

    # Combine all titles and units
    units = dict(zip(field_df["FIELD"], field_df["UNITS"]))
    titles = dict(zip(field_df["FIELD"], field_df["TITLE"]))
    field_units = {**units, **UNITS}
    titles = {**titles, **TITLES}

    # Find value ranges for color scales
    scales = get_scales(file_df, field_units)

    # For each data frame, if it is missing columns add nans in
    for path in file_df["file"]:
        df = pd.read_csv(path)
        for field in list(units.keys()) + ["nrel_region"]:
            if field not in df.columns:
                df[field] = np.nan
        df.to_csv(path, index=False)

    # Convert to a config entry
    config = {
        "data": file_df.to_dict(),
        "directory": directory,
        "units": units,
        "scales": scales,
        "titles": titles,
        "parameters": {}   # We will add an option to upload a parameter table
    }

    # Get existing/build new configuration file
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "r") as file:
            full_config = json.load(file)
    else:
        full_config = {}

    # Add in the new entry and save
    full_config[name] = config
    with open(CONFIG_PATH, "w") as file:
        file.write(json.dumps(full_config, indent=4))
