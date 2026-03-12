"""
Filename:    synoptic_maps.py
Author:      Deanna Nash, dnash@ucsd.edu
Description: Script to create maps for each day of a PFDF in CA. Option 1 is a 4-panel for 00, 06, 12, 18Z with IVT vectors/colorfill and 500 mb height. Option 2 is a 4-panel for 00, 06, 12, 18Z with SLP/IWV/925 mb wind barbs
"""

import sys, os
import xarray as xr
import pandas as pd
import numpy as np
import datetime

# import personal modules
# Path to modules
sys.path.append('modules')
from plotter import plot_four_panel_plot_ivt, plot_four_panel_plot_iwv
from read_data import read_ERA5_data_for_event

path_to_data = '/expanse/nfs/cw3e/cwp140/'
# read file with dates
with open("PFDF_dates.txt") as f:
    dates = [line.strip() for line in f if line.strip()]

# convert to dataframe
df = pd.DataFrame({"date": pd.to_datetime(dates, format="%d %b %Y")})

#######################
### Create IVT maps ###
#######################
varname_lst = ['ivt', '500z']
for index, row in df.iterrows():
    date = row['date']
    ds_lst = []
    for j, varname in enumerate(varname_lst):
        ds = read_ERA5_data_for_event(date, varname)
        ds_lst.append(ds)
    ds = xr.merge(ds_lst, compat='no_conflicts')
    plot_four_panel_plot_ivt(ds, date, 'ivt')

#######################
### Create IWV maps ###
#######################
varname_lst = ['iwv', '925uv', 'mslp']
for index, row in df.iterrows():
    date = row['date']
    ds_lst = []
    for j, varname in enumerate(varname_lst):
        ds = read_ERA5_data_for_event(date, varname)
        ds_lst.append(ds)
    ds = xr.merge(ds_lst, compat='no_conflicts')
    plot_four_panel_plot_iwv(ds, date, 'iwv')