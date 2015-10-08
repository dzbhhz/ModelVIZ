# -*- coding: utf-8 -*-
"""
Created on Thu May 23 09:10:22 2013
contour massbay fvcom
@author: zhaobin
"""

from pylab import *
from matplotlib.collections import PolyCollection
import matplotlib.tri as Tri
from mpl_toolkits.basemap import Basemap
import datetime as dt
import netCDF4
import sys
import numpy as np
from datetime import timedelta

urlname=input("input model('30yr' or 'massbay'):")
depth=int(input("input depth(negtive number):"))
TIME=input("input start time(for example:2015-9-29 0:0:0)")  #read data from file
#get different url ↓↓↓↓↓↓↓↓↓↓↓↓ 
if urlname=="30yr":  
    
    stime=dt.datetime.strptime(TIME, "%Y-%m-%d %H:%M:%S")
    timesnum=stime.year-1981
    standardtime=dt.datetime.strptime(str(stime.year)+'-01-01 00:00:00', "%Y-%m-%d %H:%M:%S")
    timedeltaprocess=(stime-standardtime).days
    startrecord=26340+35112*(timesnum/4)+8772*(timesnum%4)+1+timedeltaprocess*24     
    url = 'http://www.smast.umassd.edu:8080/thredds/dodsC/fvcom/hindcasts/30yr_gom3?temp,lon,lat,lonc,latc,time,nv,h,siglay,salinity'
else:
    TIME=dt.datetime.strptime(TIME, "%Y-%m-%d %H:%M:%S") 
    now=dt.datetime.now()
    if TIME>now:
         diff=(TIME-now).days
    else:
         diff=(now-TIME).days
    if diff>3:
        print("please check your input start time,within 3 days both side form now on")
        sys.exit(0)
    timeperiod=(TIME)-(now-timedelta(days=3))
    startrecord=(timeperiod.seconds)/60/60
    url="http://www.smast.umassd.edu:8080/thredds/dodsC/FVCOM/NECOFS/Forecasts/NECOFS_FVCOM_OCEAN_MASSBAY_FORECAST.nc?temp,lon,lat,lonc,latc,time,nv,h,siglay,salinity"
    
nc = netCDF4.Dataset(url)
lat = nc.variables['lat'][:]
lon = nc.variables['lon'][:]
latc = nc.variables['latc'][:]
lonc = nc.variables['lonc'][:]
temp=nc.variables['temp']
sali=nc.variables["salinity"]
siglay=nc.variables['siglay']
h = nc.variables['h'][:]
# read connectivity array
nv = nc.variables['nv'][:].T - 1
time_var = nc.variables['time']

# create a triangulation object, specifying the triangle connectivity array
tri = Tri.Triangulation(lon,lat, triangles=nv)
# plot depth using tricontourf
#get temperature and salinity in given depth ↓↓↓↓↓↓↓↓↓↓↓
salinity=[]
temprature=[]
for i in range(len(lon)):
    depthtotal=siglay[:,i]*h[i]
    layer=np.argmin(abs(depthtotal+depth))
    temprature.append(temp[int(startrecord),layer,i])
    salinity.append(sali[int(startrecord),layer,i])
temprature=np.array(temprature)
salinity=np.array(salinity)   

latsize=[min(lat)-0.1,max(lat)+0.1]
lonsize=[min(lon)-0.1,max(lon)+0.1]   #basemap range

fig=figure(figsize=(12,16)) #plot temperature
ax=fig.add_subplot(111)
m = Basemap(projection='cyl',llcrnrlat=min(latsize),urcrnrlat=max(latsize),\
            llcrnrlon=min(lonsize),urcrnrlon=max(lonsize),resolution='h')#,fix_aspect=False)
m.drawparallels(np.arange(int(min(latsize)),int(max(latsize))+1,3),labels=[1,0,0,0])
m.drawmeridians(np.arange(int(min(lonsize)),int(max(lonsize))+1,3),labels=[0,0,0,1])
m.drawcoastlines()
m.fillcontinents(color='grey')
m.drawmapboundary()
levels=np.arange(np.amin(temprature),np.amax(temprature),0.1)
tri_temp=tricontourf(tri,temprature,levels=levels)
colorbar(tri_temp)
plt.title(urlname+' temperature model,Depth:'+str(-depth)+'m, Time:'+str(TIME)[0:-9]) 
plt.savefig(urlname+'temperature.png')

fig1=figure(figsize=(12,16)) #plot salinity
ax1=fig1.add_subplot(111)
m = Basemap(projection='cyl',llcrnrlat=min(latsize),urcrnrlat=max(latsize),\
            llcrnrlon=min(lonsize),urcrnrlon=max(lonsize),resolution='h')#,fix_aspect=False)
m.drawparallels(np.arange(int(min(latsize)),int(max(latsize))+1,3),labels=[1,0,0,0])
m.drawmeridians(np.arange(int(min(lonsize)),int(max(lonsize))+1,3),labels=[0,0,0,1])
m.drawcoastlines()
m.fillcontinents(color='grey')
m.drawmapboundary()
levels=np.arange(28,34,0.01)
tri_sal=tricontourf(tri,salinity,levels=levels)
colorbar()
plt.title(urlname+' salinity model,Depth:'+str(-depth)+'m, Time:'+str(TIME)[0:-9]) 
plt.show()
plt.savefig(urlname+'salinity.png')
