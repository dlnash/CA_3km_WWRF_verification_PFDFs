"""
Filename:    read_data.py
Author:      Deanna Nash, dnash@ucsd.edu
Description: Function to load downloaded 6-hr ERA5 data (ivt, 500z, 925uv, iwv, and mslp)
"""

import os, sys
import pandas as pd
import xarray as xr
import numpy as np

def read_ERA5_data_for_event(date, varname):
    year = pd.to_datetime(date, format='%Y-%m-%d').year
    path_to_data = '/cw3e/mead/projects/cwp162/data/downloads/ERA5_sfc/'
    fname = path_to_data + '{0}/6hr/era5_namerica_025dg_6hr_{0}_{1}.nc'.format(varname, year)
    ds = xr.open_dataset(fname)
    ds = ds.drop_vars("expver", errors="ignore").drop_dims("expver", errors="ignore")

    if varname == "ivt":

        # mapping of possible ERA5 names → desired names
        rename_map = {
            "p72.162": "IVTv",
            "p71.162": "IVTu",
            "viwvn": "IVTv",
            "viwve": "IVTu",
            "valid_time": "time"
        }
    
        # only rename variables that exist
        rename_dict = {k: v for k, v in rename_map.items() if k in ds.variables}
    
        ds = ds.rename(rename_dict)
    
        # compute IVT magnitude
        ds = ds.assign(ivt=np.sqrt(ds.IVTu**2 + ds.IVTv**2))

    if varname == '500z':
        ## convert geopotential (m2 s-2) to geopotential height (m)
        g = 9.80665 ## gravitational acceleration m s-2
        ds['z'] = ds['z'] / g
        ds = ds.rename({'valid_time': 'time'})
        ds = ds.squeeze()

    if varname == '925uv':
        ds = ds.rename({'valid_time': 'time'})
        ds = ds.squeeze()

    if varname == 'iwv':
        ds = ds.rename({'valid_time': 'time', 'tcwv': 'iwv'})
        ds = ds.squeeze()

    if varname == 'mslp':
        ds = ds.rename({'valid_time': 'time', 'msl': 'mslp'})
        ds = ds.squeeze()
        ds['mslp'] = ds['mslp'] / 100 # convert Pa to hPa

    return ds