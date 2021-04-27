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
from review.support import get_scales

from app import app
from review import print_args
from tkinter import filedialog

# MAC Tkinter solution?
import matplotlib
matplotlib.use("TkAgg")


layout = html.Div([
    # Start of the page
    html.H3("Configure Project"),

    # Project name
    html.H5("Project Name"),
    dcc.Input(
        id="project_name",
        debounce=True,
        style={"margin-left": "50px", "margin-bottom": "15px"}
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
            placeholder="Input possible values for this group.",
            style={"width": "27.5%"}
        ),
    ], className="row",
        style={"margin-left": "50px", "margin-bottom": "15px"}
    ),
    html.Div(id="top_groups"),

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
    html.Div(id="groups",  style={"display": "none"}),
    html.Div(id="files", style={"display": "none"}),
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


@app.callback([Output("proj_input", "placeholder"),
               Output("proj_dir", "children"),
               Output("project_directory_print", "children")],
              [Input("proj_nav", "n_clicks"),
               Input("proj_input", "value")])
def find_project_directory(n_clicks, path):
    """Find the root project directory containing data files."""
    # Print variables
    trig = dash.callback_context.triggered[0]['prop_id']
    print_args(find_project_directory, n_clicks, path, trig=trig)

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
              [Input("submit_group", "n_clicks")],
              [State("group_input", "value"),
               State("group_value_input", "value"),
               State("groups", "children")])
def create_groups(submit, group_input, group_values, groups):
    """Set a group with which to categorize datasets."""
    print_args(create_groups, submit, group_input, group_values, groups)

    if groups:
        groups = json.loads(groups)
    else:
        groups = {}

    if group_input:
        groups[group_input] = group_values

    children = []
    for group, values in groups.items():
        if group:
            reminder = "{}: {}".format(group, values)
            sdiv = html.Div(
                    id="{}_options".format(group),
                    children=[
                        html.P(reminder),
                    ],
                    className="row",
                    style={"margin-left": "100px", "margin-bottom": "15px"}
                )

            children.append(sdiv)

    return children, json.dumps(groups)


@app.callback(Output("files", "children"),
              [Input("file_nav", "n_clicks"),
               Input("file_pattern", "value")],
              [State("proj_dir", "children"),
               State("files", "children")])
def add_datasets(n_clicks, pattern, initialdir, files):
    """Browse the file system for a list of file paths."""
    trig = dash.callback_context.triggered[0]['prop_id']
    print_args(add_datasets, n_clicks, pattern, initialdir, files, trig=trig)

    if files == "null" or files == "{}" or files is None:
        files = {}
        key = 0
    else:
        files = json.loads(files)
        keys = [int(k) for k in files.keys()]
        key = max(keys) + 1

    if "file_nav" in trig:
        if n_clicks > 0:
            paths = navigate("files", initialdir=initialdir)
            for path in paths:
                files[key] = os.path.join(initialdir, path)
                key += 1
                if not os.path.exists(path):
                    print("Chosen path does not exist.")  # Add OSError

    elif "file_pattern" in trig:
        paths = glob(os.path.join(initialdir, pattern), recursive=True)
        paths.sort()
        new_files = dict(zip(range(0, len(paths)), paths))
        files = {**files, **new_files}
    else:
        raise PreventUpdate

    file_list = json.dumps(files)

    return file_list


@app.callback(Output("file_groups", "children"),
              [Input("files", "children"),
               Input("proj_dir", "children"),
               Input("groups", "children")])
def set_dataset_groups(files, proj_dir, groups):
    """For each file, set a group and value from the user inputs above."""
    print_args(set_dataset_groups, files, proj_dir, groups)
    if files and files != "null" and files != '{}':
        files = json.loads(files)
        groups = json.loads(groups)
        groups = {k: v.split(",") for k, v in groups.items()}
        groups = {k: [v.split()[0] for v in g] for k, g in groups.items()}
        groups = {k: v + ["NA"] for k, v in groups.items()}

        # Dropdowns
        dropdowns = {}
        for group, options in groups.items():
            options = [{"label": op, "value": op} for op in options]
            dropdowns[group] = {
                "options": options,
                # "placeholder": str(options)
            }

        # Data Table
        files = list(files.values())
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
              [State("extra_fields", "children")])
def find_extra_fields(files, groups, fields):
    """Use one of the files to infer extra fields and assign units."""
    print_args(find_extra_fields, files, groups, fields)

    if files == "null" or files == '{}':
        raise PreventUpdate

    new_fields = []
    if files:
        files = json.loads(files)
        groups = json.loads(groups)
        files = list(files.values())
        for file in files:
            with open(files[0], "r") as f1:
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
               State("proj_input", "value"),
               State("extra_fields", "children")])
def build_config(n_clicks, groups, project_name, directory, fields):
    """Consolidate inputs into a project config and update overall config."""
    print_args(build_config, n_clicks, groups, project_name, directory, fields)

    if n_clicks == 0:
        raise PreventUpdate

    # Get the file/group and fields data frames
    field_df, fmsg = dash_to_pandas(fields)
    file_df, gmsg = dash_to_pandas(groups)

    # Get just the file name from the path
    file_df["name"] = file_df["file"].apply(lambda x: os.path.basename(x))

    # Combine all titles and units
    units = dict(zip(field_df["FIELD"], field_df["UNITS"]))
    titles = dict(zip(field_df["FIELD"], field_df["TITLE"]))
    units = {**units, **UNITS}
    titles = {**titles, **TITLES}

    # Find value ranges for color scales
    scales = get_scales(file_df, units)

    # For each data frame, if it is missing columns add nans in
    for path in file_df["file"]:
        df = pd.read_csv(path)
        for field in list(units.keys()) + ["nrel_region"]:
            print(field)
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
    full_config[project_name] = config
    with open(CONFIG_PATH, "w") as file:
        file.write(json.dumps(full_config, indent=4))
