# -*- coding: utf-8 -*-
"""Add fields to output CSVs.

NREL Regions, Configuration variables, etc

Created on Thu Jan  7 07:17:36 2021

@author: twillia2
"""
import os

import pandas as pd
import pathos.multiprocessing as mp

from review.support import Config, Data_Path
from revruns.rrprocess import Process
from tqdm import tqdm


CONFIG = Config('ATB Onshore - FY21')
DP = Data_Path(CONFIG.directory)
FILES = DP.contents("*sc.csv")
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
    """Convert region-states dictionary to state-region dictionary."""
    regions = {}
    for region, states in REGIONS.items():
        for state in states:
            regions[state] = region
    return regions


def capex(df, unit_capex=910, unit_om=38.95, fcr=0.049):
    """Recalculate capital costs if needed input columns are present."""
    capacity = df["capacity"]
    capacity_kw = capacity * 1000
    cc = capacity_kw * unit_capex
    om = unit_om * capacity_kw
    mean_cf = df["mean_cf"]
    lcoe = df["mean_lcoe"]
    cc = ((lcoe * (capacity * mean_cf * 8760)) - om) / fcr
    unit_cc = (cc / capacity) / 1000  # $/kw

    df["capex"] = cc
    df["unit_cc"] = unit_cc

    return df


def update_file(path):
    """Add fields to a single file."""
    config = CONFIG.project_config

    # Get scenario from path
    name = os.path.basename(path)
    scenario = name.replace("_sc.csv", "")

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

    # And the scenario
    df["scenario"] = scenario

    df = capex(df)

    df.to_csv(path)


def update_files():
    """Update all files with added field."""
    with mp.Pool(mp.cpu_count()) as pool:
        for _ in tqdm(pool.imap(update_file, FILES), total=len(FILES)):
            pass


if __name__ == "__main__":
    update_files()
