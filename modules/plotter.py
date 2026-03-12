"""
Filename:    plotter.py
Author:      Deanna Nash, dnash@ucsd.edu
Description: Functions for plotting
"""

# Import Python modules

import os, sys
import numpy as np
import itertools
import xarray as xr
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
import matplotlib.ticker as mticker
import colorsys
from matplotlib.colors import LinearSegmentedColormap # Linear interpolation for color maps
import matplotlib.patches as mpatches
import matplotlib.animation as animation
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
from matplotlib.projections import get_projection_class
import pandas as pd
from matplotlib.gridspec import GridSpec
from matplotlib.colorbar import Colorbar # different way to handle colorbar
import seaborn as sns
import cmocean.cm as cmo
from datetime import timedelta
import textwrap
from matplotlib.gridspec import GridSpec
import itertools ## need this for the cbarticks

## import personal modules
import cw3ecmaps as ccmaps

def plot_terrain(ax, ext):
    fname = '/expanse/nfs/cw3e/cwp140/downloads/ETOPO1_Bed_c_gmt4.grd'
    datacrs = ccrs.PlateCarree()
    grid = xr.open_dataset(fname)
    grid = grid.where(grid.z > 0) # mask below sea level
    grid = grid.sel(x=slice(ext[0], ext[1]), y=slice(ext[2], ext[3]))
    cs = ax.pcolormesh(grid.x, grid.y, grid.z,
                        cmap=cmo.gray_r, transform=datacrs, alpha=0.7)
    
    return ax
    
def draw_basemap(ax, datacrs=ccrs.PlateCarree(), extent=None, xticks=None, yticks=None, grid=False, left_lats=True, right_lats=False, bottom_lons=True, mask_ocean=False, coastline=True):
    """
    Creates and returns a background map on which to plot data. 
    
    Map features include continents and country borders.
    Option to set lat/lon tickmarks and draw gridlines.
    
    Parameters
    ----------
    ax : 
        plot Axes on which to draw the basemap
    
    datacrs : 
        crs that the data comes in (usually ccrs.PlateCarree())
        
    extent : float
        Set map extent to [lonmin, lonmax, latmin, latmax] 
        Default: None (uses global extent)
        
    grid : bool
        Whether to draw grid lines. Default: False
        
    xticks : float
        array of xtick locations (longitude tick marks)
    
    yticks : float
        array of ytick locations (latitude tick marks)
        
    left_lats : bool
        Whether to add latitude labels on the left side. Default: True
        
    right_lats : bool
        Whether to add latitude labels on the right side. Default: False
        
    Returns
    -------
    ax :
        plot Axes with Basemap
    
    Notes
    -----
    - Grayscale colors can be set using 0 (black) to 1 (white)
    - Alpha sets transparency (0 is transparent, 1 is solid)
    
    """
    ## some style dictionaries
    kw_ticklabels = {'size': 10, 'color': 'dimgray', 'weight': 'light'}
    kw_grid = {'linewidth': .5, 'color': 'k', 'linestyle': '--', 'alpha': 0.4}
    kw_ticks = {'length': 4, 'width': 0.5, 'pad': 2, 'color': 'black',
                         'labelsize': 10, 'labelcolor': 'dimgray'}

    # Use map projection (CRS) of the given Axes
    mapcrs = ax.projection    
    
    # Add map features (continents and country borders)
    ax.add_feature(cfeature.LAND, facecolor='0.9')      
    ax.add_feature(cfeature.BORDERS, edgecolor='0.4', linewidth=0.8)
    if coastline == True:
        ax.add_feature(cfeature.COASTLINE, edgecolor='0.4', linewidth=0.8)
    if mask_ocean == True:
        ax.add_feature(cfeature.OCEAN, edgecolor='0.4', zorder=12, facecolor='white') # mask ocean
        
    ## Tickmarks/Labels
    ## Add in meridian and parallels
    if mapcrs == ccrs.NorthPolarStereo():
        gl = ax.gridlines(draw_labels=False,
                      linewidth=.5, color='black', alpha=0.5, linestyle='--')
    elif mapcrs == ccrs.SouthPolarStereo():
        gl = ax.gridlines(draw_labels=False,
                      linewidth=.5, color='black', alpha=0.5, linestyle='--')
        
    else:
        gl = ax.gridlines(crs=datacrs, draw_labels=True, **kw_grid)
        gl.top_labels = False
        gl.left_labels = left_lats
        gl.right_labels = right_lats
        gl.bottom_labels = bottom_lons
        gl.xlocator = mticker.FixedLocator(xticks)
        gl.ylocator = mticker.FixedLocator(yticks)
        gl.xformatter = LONGITUDE_FORMATTER
        gl.yformatter = LATITUDE_FORMATTER
        gl.xlabel_style = kw_ticklabels
        gl.ylabel_style = kw_ticklabels
    
    ## Gridlines
    # Draw gridlines if requested
    if (grid == True):
        gl.xlines = True
        gl.ylines = True
    if (grid == False):
        gl.xlines = False
        gl.ylines = False
            

    # apply tick parameters
    ax.set_xticks(xticks, crs=datacrs)
    ax.set_yticks(yticks, crs=datacrs)
    plt.yticks(color='w', size=1) # hack: make the ytick labels white so the ticks show up but not the labels
    plt.xticks(color='w', size=1) # hack: make the ytick labels white so the ticks show up but not the labels
    ax.ticklabel_format(axis='both', style='plain')

    ## Map Extent
    # If no extent is given, use global extent
    if extent is None:        
        ax.set_global()
        extent = [-180., 180., -90., 90.]
    # If extent is given, set map extent to lat/lon bounding box
    else:
        ax.set_extent(extent, crs=datacrs)
    
    return ax

def plot_four_panel_plot_ivt(ds, event_date, varname):
    
    # Set up projection
    datacrs = ccrs.PlateCarree()  ## the projection the data is in
    mapcrs = ccrs.PlateCarree() ## the projection you want your map displayed in
    ext = [-140., -110., 20, 50]

    # Set tick/grid locations
    tx = 10
    ty = 5
    dx = np.arange(ext[0],ext[1]+tx,tx)
    dy = np.arange(ext[2],ext[3]+ty,ty)

    nrows = 3
    ncols = 2
    
    ## Use gridspec to set up a plot with a series of subplots that is
    ## n-rows by n-columns
    gs = GridSpec(nrows, ncols, height_ratios=[1, 1, 0.05], width_ratios = [1, 1], wspace=0.01, hspace=0.2)
    ## use gs[rows index, columns index] to access grids
    
    fig = plt.figure(figsize=(8, 9.))
    fig.dpi = 300
    fname = f'figs/{varname}/{varname}_map_{event_date}'
    fmt = 'png'

    ## loop through time step
    row_idx = [0, 0, 1, 1]
    col_idx = [0, 1, 0, 1]
    llats = [True, False]*2
    blons = [False, False, True, True]
    date_lst = pd.date_range(event_date, periods=4, freq="6h")
    tmp = ds.sel(time=date_lst)
    
    for i, date, in enumerate(tmp.time.values):
        ax = fig.add_subplot(gs[row_idx[i], col_idx[i]], projection=mapcrs)
    
        ax = draw_basemap(ax, extent=ext, xticks=dx, yticks=dy,
                          left_lats=llats[i], right_lats=False, bottom_lons=blons[i])
        ax.set_extent(ext, datacrs)
        ax.add_feature(cfeature.STATES, edgecolor='0.4', linewidth=0.8)

        # add titles
        title = pd.to_datetime(date).strftime('%H UTC %d %b %Y')
        ax.set_title(title, loc='left')
    
        ## add filled contours
        ivt = tmp.sel(time=date)
        cmap, norm, bnds, cbarticks, cbarlbl = ccmaps.cmap(varname) # get cmap from our custom function
        cf = ax.contourf(ivt.longitude.values, ivt.latitude.values, ivt.ivt.values, transform=datacrs,
                         levels=bnds, cmap=cmap, norm=norm, alpha=0.9)

        ## add contour lines
        # Contour Lines
        hgts = ivt.z.values / 10 # convert to dam
        print(hgts.min(), hgts.max())
        clevs = np.arange(0, 1000, 4)
        cs = ax.contour(ivt.longitude.values, ivt.latitude.values, hgts, transform=datacrs,
                        levels=clevs, colors='grey', linewidths=0.7)
        
        kw_clabels = {'fontsize': 8.5, 'inline': True, 'inline_spacing': 5, 'fmt': '%i', 'rightside_up': True, 'use_clabeltext': True}
        cl = ax.clabel(cs, clevs[::2], **kw_clabels)
        for txt in cl:
                    txt.set_bbox(dict(facecolor='white', edgecolor='none', pad=0.5))

        # Wind barbs / vectors 
        uvec_mask = ivt.IVTu.where((ivt.ivt >=250.)).values # mask values where IVT magnitude is less than 250 kg m-1 s-1
        vvec_mask = ivt.IVTv.where((ivt.ivt >=250.)).values # mask values where IVT magnitude is less than 250 kg m-1 s-1
        
        Q = ax.quiver(ivt.longitude.values, ivt.latitude.values, uvec_mask, vvec_mask, transform=datacrs, 
                  color='k', regrid_shape=30,
                  angles='xy', scale_units='xy', scale=500, units='xy')

    # quiver key
    qk = ax.quiverkey(Q, 0.8, -0.1, 250, '250 kg/m/s', labelpos='E',
                      coordinates='axes', fontproperties={'size': 6.0})

    # Add color bar
    cbax = plt.subplot(gs[-1, :]) # colorbar axis (last row, all columns)
    cbarticks = list(itertools.compress(bnds, cbarticks)) ## this labels the cbarticks based on the cmap dictionary
    cb = Colorbar(ax = cbax, mappable = cf, orientation = 'horizontal', ticklocation = 'bottom', ticks=cbarticks)
    cb.set_label(cbarlbl, fontsize=11)
    cb.ax.tick_params(labelsize=12)
    
    fig.savefig('%s.%s' %(fname, fmt), bbox_inches='tight', dpi=fig.dpi, transparent=True)
    fig.clf()

def plot_four_panel_plot_iwv(ds, event_date, varname):

    # Set up projection
    datacrs = ccrs.PlateCarree()  ## the projection the data is in
    mapcrs = ccrs.PlateCarree() ## the projection you want your map displayed in
    ext = [-140., -110., 20, 50]

    # Set tick/grid locations
    tx = 10
    ty = 5
    dx = np.arange(ext[0],ext[1]+tx,tx)
    dy = np.arange(ext[2],ext[3]+ty,ty)

    nrows = 3
    ncols = 2
    
    ## Use gridspec to set up a plot with a series of subplots that is
    ## n-rows by n-columns
    gs = GridSpec(nrows, ncols, height_ratios=[1, 1, 0.05], width_ratios = [1, 1], wspace=0.01, hspace=0.2)
    ## use gs[rows index, columns index] to access grids
    
    fig = plt.figure(figsize=(8, 9.))
    fig.dpi = 300
    fname = f'figs/{varname}/{varname}_map_{event_date}'
    fmt = 'png'

    ## loop through time step
    row_idx = [0, 0, 1, 1]
    col_idx = [0, 1, 0, 1]
    llats = [True, False]*2
    blons = [False, False, True, True]
    date_lst = pd.date_range(event_date, periods=4, freq="6h")
    tmp = ds.sel(time=date_lst)
    
    for i, date, in enumerate(tmp.time.values):
        ax = fig.add_subplot(gs[row_idx[i], col_idx[i]], projection=mapcrs)
    
        ax = draw_basemap(ax, extent=ext, xticks=dx, yticks=dy,
                          left_lats=llats[i], right_lats=False, bottom_lons=blons[i])
        ax.set_extent(ext, datacrs)
        ax.add_feature(cfeature.STATES, edgecolor='0.4', linewidth=0.8)

        # add titles
        title = pd.to_datetime(date).strftime('%H UTC %d %b %Y')
        ax.set_title(title, loc='left')
    
        ## add filled contours
        iwv = tmp.sel(time=date)
        cmap, norm, bnds, cbarticks, cbarlbl = ccmaps.cmap(varname) # get cmap from our custom function
        cf = ax.contourf(iwv.longitude.values, iwv.latitude.values, iwv.iwv.values, transform=datacrs,
                         levels=bnds, cmap=cmap, norm=norm, alpha=0.9)

        ## add contour lines
        # Contour Lines
        mslp = iwv.mslp.values
        clevs = np.arange(0, 1500, 4)
        cs = ax.contour(iwv.longitude.values, iwv.latitude.values, mslp, transform=datacrs,
                        levels=clevs, colors='grey', linewidths=0.7)
        
        kw_clabels = {'fontsize': 8.5, 'inline': True, 'inline_spacing': 5, 'fmt': '%i', 'rightside_up': True, 'use_clabeltext': True}
        cl = ax.clabel(cs, clevs[::2], **kw_clabels)
        for txt in cl:
                    txt.set_bbox(dict(facecolor='white', edgecolor='none', pad=0.5))

        # Wind barbs / vectors 
        Q = ax.quiver(iwv.longitude.values, iwv.latitude.values, iwv.u.values, iwv.v.values, transform=datacrs, 
                  color='k', regrid_shape=30,
                  angles='xy', scale_units='xy', scale=15, units='xy')

    # quiver key
    qk = ax.quiverkey(Q, 0.8, -0.1, 10, '10 m/s', labelpos='E',
                      coordinates='axes', fontproperties={'size': 6.0})

    # Add color bar
    cbax = plt.subplot(gs[-1, :]) # colorbar axis (last row, all columns)
    cb = Colorbar(ax = cbax, mappable = cf, orientation = 'horizontal', ticklocation = 'bottom', ticks=cbarticks)
    cb.set_label(cbarlbl, fontsize=11)
    cb.ax.tick_params(labelsize=12)
    
    fig.savefig('%s.%s' %(fname, fmt), bbox_inches='tight', dpi=fig.dpi, transparent=True)
    fig.clf()