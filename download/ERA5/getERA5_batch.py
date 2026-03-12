"""
Filename:    getERA5_batch.py
Author:      Tessa Montini, tmontini@ucsb.edu & Deanna Nash, dnash@ucsd.edu
Description: Download ERA5 data based on input configuration dictionary.
             Use in conjunction with ERA5_config.yml for input variables.
"""

import sys
import cdsapi
import yaml
from pathlib import Path


# -----------------------------
# Read configuration
# -----------------------------
config_name = sys.argv[1]
print(f"Using config: {config_name}")

yaml_doc = "ERA5_config.yml"

print("Open config file")
with open(yaml_doc) as f:
    config = yaml.safe_load(f)

ddict = config[config_name]


# -----------------------------
# Setup output directory
# -----------------------------
datadir = Path(ddict["datadir"])
datadir.mkdir(parents=True, exist_ok=True)


# -----------------------------
# Create CDS API client once
# -----------------------------
c = cdsapi.Client()


# -----------------------------
# Loop through years
# -----------------------------
print("START LOOP THROUGH YEARS")

for yr in range(ddict["start_yr"], ddict["end_yr"] + 1):

    print(f"... {yr}")

    outfile = datadir / f"{ddict['fprefix']}_{yr}.nc"

    # ---------------------------------
    # Skip download if file exists
    # ---------------------------------
    if outfile.exists():
        print(f"File exists, skipping: {outfile}\n")
        continue

    # ---------------------------------
    # Build request dictionary
    # ---------------------------------
    request = {
        "product_type": "reanalysis",
        "variable": ddict["var_name"],
        "year": f"{yr}",
        "month": ddict["month"],
        "day": ddict["day"],
        "time": ddict["time"],
        "area": ddict["area"],
        "grid": ddict["grid"],
        "format": "netcdf",
    }

    # Add pressure levels only if needed
    if ddict["data_type"] == "reanalysis-era5-pressure-levels":
        request["pressure_level"] = ddict["levels"]

    # ---------------------------------
    # Download
    # ---------------------------------
    print(f"Downloading: {outfile}")
    c.retrieve(ddict["data_type"], request, str(outfile))

    print(f"Download complete: {outfile}\n")