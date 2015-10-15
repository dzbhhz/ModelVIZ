# -*- coding: utf-8 -*-
"""
Created on Mon Mar 23 13:38:10 2015
input time and lat,lon.plot vertical transect of ROMS,FVCOM,HYCOM`s temperature from shallow to deep
@author: zhaobin
"""

import pandas as pd
import numpy as np
from mpl_toolkits.basemap import Basemap
import netCDF4
import matplotlib.pyplot as plt
from my_modules import draw_basemap,dist
from matplotlib.mlab import griddata
from datetime import datetime,timedelta
def getHYcom(latpt,lonpt,time_roms,depth):
    '''old version
    lonpt=360+lonpt+74.160034         #this is HYCOM`S LON range
    if time.month==1 and time.day==1:
        url='http://tds.hycom.org/thredds/dodsC/datasets/global/GLBa0.08_rect/data/temp/rarchv.'+str(time.year)+'_001_00_3zt.nc' 
    else:
        url='http://tds.hycom.org/thredds/dodsC/datasets/global/GLBa0.08_rect/data/temp/rarchv.'+str(time.year)+'_'+format(int(str(time-datetime(time.year,1,1,)).split(' ')[0])+1,'03')+'_00_3zt.nc'
        #use different days setting url
    '''   
    url='http://tds.hycom.org/thredds/dodsC/GLBu0.08/expt_19.1/3hrly'
    nc = netCDF4.Dataset(url)
    lat = nc.variables['lat'][1400:1550] 
    lon = nc.variables['lon'][1250:1450]  # ROMS range 
    Depth = nc.variables['depth'][:]
    t=nc.variables['time'][:]
    layer=[]
    for i in depth[0:len(depth)+1]:
        layer.append(np.argmin(abs(i-Depth)))     #get layer of depth
    dist_sq=[]
    indlat,indlon=[],[]
    for k in range(len(lat)):
        for j in range(len(lon)):
            dist_sq.append((lat[k]-latpt)**2 + (lon[j]-lonpt)**2)  # find squared distance of every point on grid
            indlat.append(k)
            indlon.append(j)
    id = np.array(dist_sq).argmin() # 1D index of minimum dist_sq element
    t_diff=(time_roms-datetime(2000,1,1)).total_seconds()/3600     #2000,01,01 is HYCOM`s start time.Unit is hour.
    TIME=np.argmin(abs(t_diff-np.array(t)))
    var=[]
    for i in layer:
        t = nc.variables['water_temp'][TIME,i,1400+indlat[id],1250+indlon[id]] #creates a "netCDF4 object"
        var.append(t)
    nc.close()
    return var
    
def getFVcom(latpt,lonpt,time_roms,depth_roms):
    url='http://www.smast.umassd.edu:8080/thredds/dodsC/fvcom/hindcasts/30yr_gom3/mean'
    nc = netCDF4.Dataset(url)
    lat = nc.variables['lat'][:]
    lon = nc.variables['lon'][:]
    Depth = nc.variables['h'][:]
    siglay=nc.variables['siglay'][:]
    time=nc.variables['time'][:]
    modtemp=nc.variables['temp'] 
    modtime=[]
    for i in range(len(time)):
        t=timedelta(days=float(time[i])).total_seconds()
        modtime.append(t)                        #change time days to seconds
    depth=(-Depth*siglay).transpose()                #each layer`s depth
    distance=dist(lonpt,latpt,lon,lat)
    node=np.argmin(distance)                 #get nearest node
    layer=[]
    for i in depth_roms[0:len(depth_roms)+1]:
        layer.append(np.argmin(abs(i-depth[node])))   #get layer of depth
    t_diff=(time_roms-datetime(1858,11,17)).total_seconds()     #1858,11,17 is FVCOM`s start time
    TIME=np.argmin(abs(t_diff-np.array(modtime)))
    Temp=[]
    for i in range(len(layer)):
        t=modtemp[TIME][i][node]
        Temp.append(t)
    Temp.reverse()
    return Temp
######################################################################
temp_interval=0.5            #colorbar interval
url_roms='http://tds.marine.rutgers.edu:8080/thredds/dodsC/roms/espresso/2009_da/avg'
data = netCDF4.Dataset(url_roms)
lons_roms, lats_roms = data.variables['lon_rho'][:], data.variables['lat_rho'][:]
temps_roms=data.variables['temp']
h_roms=data.variables['h'][:]
s_rho=data.variables['s_rho'][:]
time=data.variables['ocean_time'][:]
input_value=input('please input time(for example:2010,8,3,17,0,0):')
input_time=datetime.strptime(input_value,"%Y,%m,%d,%H,%M,%S")
t_diff=(input_time-datetime(2006,1,1)).total_seconds()     #2006,1,1 is model start time
TIME=np.argmin(abs(t_diff-np.array(time)))
TIME_roms=datetime(2006,1,1)+timedelta(seconds=int(time[TIME]))
input_value_0_lon=float(input('please input start site lon(for example:-72.83):'))
input_value_0_lat=float(input('please input start site lat(for example: 40.57):'))
input_value_1_lon=float(input('please input end site lon(for example:-71.72):'))
input_value_1_lat=float(input('please input end site lon(for example: 40.09):'))
LON_interval,LAT_interval=(input_value_1_lon-input_value_0_lon)/10.0,(input_value_1_lat-input_value_0_lat)/10.0
LON,LAT=np.arange(input_value_0_lon,input_value_1_lon,LON_interval),np.arange(input_value_0_lat,input_value_1_lat,LAT_interval)

LAT_roms=[]
LON_roms=[]
H_roms=[]
Temp_roms=[]
for i in range(len(LON)):    
    temp_roms=[]
    distance=dist(LON[i],LAT[i],lons_roms, lats_roms)
    node=np.argmin(distance)                 #get nearest node
    index_one,index_two=int(node/len(lons_roms[0])),node%len(lons_roms[0])
    LAT_roms.append(lats_roms[index_one,index_two])
    LON_roms.append(lons_roms[index_one,index_two])
    H_roms.append(h_roms[index_one,index_two])       
    for j in range(len(s_rho)):                              #this is roms`s layers
        temp_roms.append(temps_roms[TIME][j][index_one,index_two])
    Temp_roms.append(temp_roms)

ttt_roms=np.array(Temp_roms).transpose()

hh_roms=[]
for i in H_roms:
    hh_roms.append(-i*s_rho)
hh=np.array(hh_roms).transpose()
distance=list(np.array([dist(LON_roms[0],LAT_roms[0],LON_roms[-1],LAT_roms[-1])])/len(LAT_roms)*range(1,len(LAT_roms)+1))   #this is distance between location
distances=[]
for i in range(len(s_rho)):
    distances.append(distance)

temp_hycom=[]
for i in range(len(LON_roms)):
    t=getHYcom(LAT_roms[i],LON_roms[i],TIME_roms,hh_roms[i])
    temp_hycom.append(t)
ttt_hycom=np.array(temp_hycom).transpose()

temp_fvcom=[]
for i in range(len(LON_roms)):
    t=getFVcom(LAT_roms[i],LON_roms[i],TIME_roms,hh_roms[i])
    temp_fvcom.append(t)
ttt_fvcom=np.array(temp_fvcom).transpose()

TEMP_roms,TEMP_fvcom,TEMP_hycom,DEPTH,DIST=[],[],[],[],[]
for i in range(len(ttt_roms)):
    for j in range(len(ttt_roms[0])):
        TEMP_roms.append(ttt_roms[i][j])
        TEMP_fvcom.append(ttt_fvcom[i][j])
        TEMP_hycom.append(ttt_hycom[i][j])
        DEPTH.append(hh[i][j])
        DIST.append(distances[i][j])

lonsize = [np.amin(lons_roms), np.amax(lons_roms)]
latsize = [np.amin(lats_roms), np.amax(lats_roms)]
dis_i = np.linspace(distance[0],distance[-1],1000)
dep_i = np.linspace(H_roms[-1],0,1000) 
modtemp_i_roms = griddata(np.array(DIST),np.array(DEPTH),np.array(TEMP_roms),dis_i,dep_i,interp='linear')
modtemp_i_fvcom = griddata(np.array(DIST),np.array(DEPTH),np.array(TEMP_fvcom),dis_i,dep_i,interp='linear')
modtemp_i_hycom = griddata(np.array(DIST),np.array(DEPTH),np.array(TEMP_hycom),dis_i,dep_i,interp='linear')
Temp_hycom=[]
for i in TEMP_hycom:
    if i>0:
        Temp_hycom.append(i)        #get rid of bad data
modtemp_i=[modtemp_i_roms,modtemp_i_fvcom,modtemp_i_hycom]

TEMP=[TEMP_roms,TEMP_fvcom,Temp_hycom]
temp_max,temp_min=[],[]
for i in range(len(TEMP)):
    MAX=np.amax(TEMP[i])
    MIN=np.amin(TEMP[i])
    temp_max.append(MAX)
    temp_min.append(MIN)       #let three pictures use one legend
MODEL=['ROMS','FVCOM','HYCOM']
fig = plt.figure()
ax = fig.add_subplot(111)
draw_basemap(fig, ax, lonsize, latsize)
plt.scatter(LON_roms,LAT_roms)
fig = plt.figure()
for i in range(len(modtemp_i)):
    ax = fig.add_subplot(1,3,i+1)
    CS = ax.contourf(dis_i, dep_i, modtemp_i[i], np.arange(int(min(temp_min)),int(max(temp_max))+2,temp_interval), cmap=plt.cm.rainbow,
                  vmax=modtemp_i[i].max(), vmin=modtemp_i[i].min())     #+2 wants to make range of colorbar bigger than  range of temperature
    ax.plot(distance,H_roms)
    plt.ylim([int(max(dep_i))+2,int(min(dep_i))-2])
    plt.xlim([min(distance),max(distance)])
    plt.xlabel('Distance(km)',fontsize=20)
    if i==0:
        plt.ylabel('Depth(m)',fontsize=20)
    plt.text(20,180,str(datetime(2006,1,1,0,0,0)+timedelta(seconds=int(time[TIME]))))   #20,180 is location of text
    polygon=[]
    for j in range(len(H_roms)):
        polygon.append([distance[j],H_roms[j]])
    polygon.append([min(distance),200])
    pg=plt.Polygon(polygon,color='white')  
    ax.add_patch(pg)                                 
    plt.title(''+MODEL[i]+' transect',fontsize=20)
cbar=plt.colorbar(CS)
cbar.ax.tick_params(labelsize=20)
cbar.ax.set_ylabel('Temperature($^\circ$C)', fontsize=20)
plt.show()
