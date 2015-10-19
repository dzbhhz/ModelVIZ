# -*- coding: utf-8 -*-
"""
Created on Mon Oct 19 11:01:24 2015
plot grid of model
@author: zdong
"""
import netCDF4
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from my_modules import draw_basemap
#####################################################
option1=input('please input which model you want to plot(ROMS or FVCOM):')
if option1=='ROMS':
    url='http://tds.marine.rutgers.edu:8080/thredds/dodsC/roms/espresso/2009_da/his'
    nc=netCDF4.Dataset(url)
    lon=nc.variables['lon_rho'][:]
    lat=nc.variables['lat_rho'][:]
    lonsize=[np.amin(lon),np.amax(lon)]
    latsize=[np.amin(lat),np.amax(lat)]
    fig=plt.figure()
    ax=fig.add_subplot(111)
    draw_basemap(fig,ax,lonsize,latsize)
    for i in range(len(lon)):
        plt.plot([lon[i][0], lon[i][129]], [lat[i][0], lat[i][129]],color='r')
    for i in range(len(lon[0])):
        plt.plot([lon[0][i], lon[81][i]], [lat[0][i], lat[81][i]],color='r') 
    plt.title('ROMS EXPRESSO',fontsize=25)
if option1=='FVCOM':
    option2=input('please input which area you want to plot(GOM3 or MASSBAY):')
    if option2=='GOM3':
        url='http://www.smast.umassd.edu:8080/thredds/dodsC/fvcom/hindcasts/30yr_gom3/mean'
        nc=netCDF4.Dataset(url)
        lon=nc.variables['lon'][:]
        lat=nc.variables['lat'][:]
        nbsn=nc.variables['nbsn'][:]  #nodes surrounding each node
        lonsize=[np.amin(lon),np.amax(lon)]
        latsize=[np.amin(lat),np.amax(lat)]
        node_s=[]
        for i in range(len(lon)):
            node_s.append(nbsn[:,i].T-1)  #get nearest index of nodes
        lons,lats=[],[]    
        for i in range(len(lon)):
            lons.append([])
            lats.append([])
            for j in range(len(node_s[i])):
                if node_s[i][j]!=-1 and node_s[i][j]!=i:
                    lons[i].append(lon[node_s[i][j]])
                    lats[i].append(lat[node_s[i][j]]) #get nearest lat,lon of nodes
        fig=plt.figure()
        ax=fig.add_subplot(111)
        draw_basemap(fig,ax,lonsize,latsize)
        for i in range(len(lon)):
            for j in range(len(lons[i])):
                plt.plot([lon[i],lons[i][j]],[lat[i],lats[i][j]],color='r')  
        plt.title('FVCOM GOM3',fontsize=25)
    if option2=='MASSBAY':
        url='http://www.smast.umassd.edu:8080/thredds/dodsC/fvcom/hindcasts/30yr_gom3/mean'
        nc=netCDF4.Dataset(url)
        lon=nc.variables['lon'][:]
        lat=nc.variables['lat'][:]
        nbsn=nc.variables['nbsn'][:]  #nodes surrounding each node
        lonsize=[-71.19001, -69.397316]
        latsize=[40.944496, 43.305405]   #range of massbay
        node_s=[]
        for i in range(len(lon)):
            node_s.append(nbsn[:,i].T-1)  #get nearest index of nodes
        lons,lats=[],[]    
        for i in range(len(lon)):
            lons.append([])
            lats.append([])
            for j in range(len(node_s[i])):
                if node_s[i][j]!=-1 and node_s[i][j]!=i:
                    lons[i].append(lon[node_s[i][j]])
                    lats[i].append(lat[node_s[i][j]])   #get nearest lat,lon of nodes
        url_m='http://www.smast.umassd.edu:8080/thredds/dodsC/FVCOM/NECOFS/Forecasts/NECOFS_FVCOM_OCEAN_MASSBAY_FORECAST.nc'
        nc_m=netCDF4.Dataset(url_m)
        lon_m=nc_m.variables['lon'][:]
        lat_m=nc_m.variables['lat'][:]
        fig=plt.figure()
        ax=fig.add_subplot(111)
        draw_basemap(fig,ax,lonsize,latsize,interval_lon=1, interval_lat=1)
        for i in range(len(lon)):
            for j in range(len(lons[i])):
                plt.plot([lon[i],lons[i][j]],[lat[i],lats[i][j]],color='r')  
        plt.plot(lon_m[0:124],lat_m[0:124],color='b',linewidth='10') #plot massbay range
        plt.title('FVCOM MASSBAY',fontsize=25)
plt.show()
