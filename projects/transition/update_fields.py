# -*- coding: utf-8 -*-
"""Add fields to output CSVs.

NREL Regions, Configuration variables, etc

Created on Thu Jan  7 07:17:36 2021

@author: twillia2
"""
import json
import os

import pandas as pd

from revruns import rr
from tqdm import tqdm


DP = rr.Data_Path(".")

FILES = DP.contents("*sc.csv")

CONFIG = os.path.expanduser("~/.review_config")

REGIONS = {
    "Pacific": [
        "Oregon",
        "Washington"
    ],
    "Mountain": [
        "Colorado",
        "Idaho",
        "Montana",
        "Wyoming"
    ],
    "Great Plains": [
        "Iowa",
        "Kansas",
        "Missouri",
        "Minnesota",
        "Nebraska",
        "North Dakota",
        "South Dakota"
    ],
    "Great Lakes": [
        "Illinois",
        "Indiana",
        "Michigan",
        "Ohio",
        "Wisconsin"
    ],
    "Northeast": [
        "Connecticut",
        "New Jersey",
        "New York",
        "Maine",
        "New Hampshire",
        "Massachusetts",
        "Pennsylvania",
        "Rhode Island",
        "Vermont"
    ],
    "California": [
        "California"
    ],
    "Southwest": [
        "Arizona",
        "Nevada",
        "New Mexico",
        "Utah"
    ],
    "South Central": [
        "Arkansas",
        "Louisiana",
        "Oklahoma",
        "Texas"
    ],
    "Southeast": [
        "Alabama",
        "Delaware",
        "District of Columbia",
        "Florida",
        "Georgia",
        "Kentucky",
        "Maryland",
        "Mississippi",
        "North Carolina",
        "South Carolina",
        "Tennessee",
        "Virginia",
        "West Virginia"
    ]
}


def reshape_regions():
    regions = {}
    for region, states in REGIONS.items():
        for state in states:
            regions[state] = region
    return regions


def update_file(path, config):
    """Add fields to a single file."""
    # Get scenario from path
    name = os.path.basename(path)
    scenario = name.split("_")[1]

    # Get the extra fields from the project configuration
    file_df = pd.DataFrame(config["data"])
    groups = [c for c in file_df.columns if c not in ["name", "file"]]
    entry = file_df[file_df["name"] == name]
    entry = entry[groups].to_dict("list")

    # Now read in the data frame and append these values
    df = pd.read_csv(path)
    for key, value in entry.items():
        value = value[0]
        df[key] = value

    # Now add NREL regions
    regions = reshape_regions()
    df["nrel_region"] = df["state"].map(regions)

    df.to_csv(path, index=False)


def update_files():
    with open(CONFIG, "r") as file:
        full_config = json.load(file)
    config = full_config["Transition"]
    for path in tqdm(FILES):
        update_file(path, config)


if __name__ == "__main__":
    update_files()
