#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Configuration Application

Created on Sun Aug 23 16:27:25 2020

@author: travis
"""

import json
import os

import dash
import dash_core_components as dcc
import dash_html_components as html
import tkinter as tk

from dash.dependencies import Input, Output, State

from app import app
from revruns.rr import Data_Path
from tkinter import filedialog
# from tkinter import ttk


DP = Data_Path("/")

DIRS = [{"label": f, "value": f} for f in DP.folders()]


layout = html.Div([

    html.H3("Configure Datasets"),

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
        dcc.Input(
            id="proj_input",
            placeholder="/",
            name="name_test",
            debounce=True,
            style={"width": "30%"}
            ),

        html.Button(
            children="navigate",
            title="navigate the file system for the project directory",
            id="proj_nav",
            n_clicks=0
            ),

    ], className="row",
        style={"margin-left": "50px"}
    ),


    # Groups
    html.H5("Create Groups", style={"margin-top": "50px"}),
    html.Div([
        dcc.Input(
            id="group_input"
        ),
        html.Button(
            children="Add Group",
            id="submit_group"
        )
    ], className="row",
        style={"margin-left": "50px", "margin-bottom": "15px"}
    ),

    html.Div(
        id="top_groups"
    ),

    # Dataset paths
    html.H5("Add Data Set(s)", style={"margin-top": "50px"}),
    html.Div([

        html.Button(
            id="file_nav",
            children="navigate",
            title="navigate the file system for a reV supply curve data set.",
            n_clicks=0
            ),

    ], className="row",
        style={"margin-left": "50px", "margin-bottom": "15px"}),

    html.Div(
        id="file_groups",
        style={"margin-bottom": "50px", "margin-left": "50px"}
    ),

    # Storage Units
    html.Div(id="proj_dir", style={"display": "none"}, children="/"),
    html.Div(id="groups",  style={"display": "none"}),
    html.Div(id="files", style={"display": "none"})
    
], className= "twelve columns")


def navigate(which, initialdir="/"):
    
    # font = ('courier', 10, 'bold')
    filetypes=[('ALL', '*'), ('CSV', '*.csv')]

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
               Output("proj_dir", "children")],
              [Input("proj_nav", "n_clicks"),
               Input("proj_input", "value")])
def find_dir(n_clicks, path):

    trig = dash.callback_context.triggered[0]['prop_id']

    if "proj_nav" in trig:
        if n_clicks > 0:
            path = navigate("folders")

    if path:
        if not os.path.exists(path):
            print("Chosen path does not exist.")
    else:
        path = "/"

    return path, path


@app.callback([Output("top_groups", "children"),
               Output("groups", "children")],
              [Input("submit_group", "n_clicks")],
              [State("group_input", "value"),
               State("groups", "children")])
def set_group(submit, group_input, groups):
    
    if groups:
        groups = json.loads(groups)
        if groups:
            key = max([int(k) for k in groups.keys()]) + 1
        else:
            key = 0
    else:
        groups = {}
        key = 0

    if group_input:
        groups[key] = group_input

    children = []
    for key, group in groups.items():
        if group:
            sdiv = html.Div(
                    id="{}_options".format(key),
                    children=[
                        html.P(group),
                        dcc.Input(
                            id="{}_input".format(key)
                        ),
                        html.Button(
                            children="Add Subgroup",
                            id="submit_{}".format(key)
                        )
                ], className="row",
                    style={"margin-left": "100px", "margin-bottom": "15px"}
                )

            children.append(sdiv)

    with open("current_groups.json", "w") as file:
        file.write(json.dumps(groups))

    return children, json.dumps(groups)




# @app.callback([Output("{}_options".format(i), "children"),
#                Output("groups", "children")],
#               [Input("submit_{}".format(i), "n_clicks")],
#               [State("{}_input".format(i), "value"),
#                 State("groups", "children")])
# def set_subgroup(submit, group_input, groups):
#     """
#     Review https://community.plotly.com/t/dynamic-controls-and-dynamic-output-components/5519
#     """
    # if groups:
    #     groups = json.loads(groups)
    # else:
    #     groups = {}
    
    # if group_input:
    #     key = group_input.lower().replace(" ", "_")
    #     groups[key] = group_input
    
    # children = []
    # for key, group in groups.items():
    #     if group:
    #         sdiv = html.Div([
    #             html.P(group, className="two columns"),
    #             dcc.Input(
    #                 id=group_input,
    #                 debounce=True,
    #                 type="text",
    #                 placeholder="Description? Units?",
    #                 className="two columns",
    #                 style={"height": "100%", "margin-left": -5}
    #                 )                
    #         ], className="row")
    #         children.append(sdiv)
    
    # return children, json.dumps(groups)


@app.callback(Output("files", "children"),
              [Input("file_nav", "n_clicks"),
               Input("proj_dir", "children")],
              [State("files", "children")])
def find_files(n_clicks, initialdir, files):

    trig = dash.callback_context.triggered[0]['prop_id']

    print("INITIALDIR: " + initialdir)

    if "file_nav" in trig:
        if n_clicks > 0:
            paths = navigate("files", initialdir=initialdir)

            if files:
                files = json.loads(files)
                keys = [int(k) for k in files.keys()]
                key = max(keys) + 1
            else:
                files = {}
                key = 0
    
            for path in paths:
    
                files[key] = os.path.join(initialdir, path)
                key += 1
    
                if not os.path.exists(path):
                    print("Chosen path does not exist.")  # How to warn?
    
            print("FIND_FILES PATH: " + str(paths))
    
            return json.dumps(files)


@app.callback(Output("file_groups", "children"),
              [Input("files", "children"),
               Input("proj_dir", "children")],
              [State("groups", "children")])
def file_groups(files, proj_dir, groups):

    if files:
        files = json.loads(files)
        groups = json.loads(groups)
        children = []
        group_options = []
        for key, group in groups.items():
            option = {"label": group, "value": key}
            group_options.append(option)

        for key, file in files.items():
            file = file.replace(proj_dir, "")
            if file[:1] == "/":
                file = file[1:]
            sdiv = html.Div([
                        html.P(file, className="two columns"),
                        dcc.Dropdown(
                            id="{}_group".format(key),
                            placeholder="Group",
                            options=group_options,
                            className="two columns",
                            style={"height": "100%"}
                            )                
                    ], className="row")
            children.append(sdiv)

        return children
