# -*- coding: utf-8 -*-
"""
Created on Fri Oct  9 11:14:17 2015

@author: zdong
"""

from mpl_toolkits.basemap import Basemap
from pylab import *
from matplotlib.mlab import griddata
import matplotlib.pyplot as plt
import datetime as dt
import netCDF4
from matplotlib import animation
import matplotlib.tri as Tri
import numpy as np
import os

def draw_basemap(fig, ax, lonsize, latsize, interval_lon=2, interval_lat=2):
    ax = fig.sca(ax)
    dmap = Basemap(projection='cyl',
                   llcrnrlat=min(latsize)-0.01,
                   urcrnrlat=max(latsize)+0.01,
                   llcrnrlon=min(lonsize)-0.01,
                   urcrnrlon=max(lonsize)+0.01,
                   resolution='h',ax=ax)
    dmap.drawparallels(np.arange(int(min(latsize)),
                                 int(max(latsize))+1,interval_lat),
                       labels=[1,0,0,0], linewidth=0,fontsize=20)
    dmap.drawmeridians(np.arange(int(min(lonsize))-1,
                                 int(max(lonsize))+1,interval_lon),
                       labels=[0,0,0,1], linewidth=0,fontsize=20)
    dmap.drawcoastlines()
    dmap.fillcontinents(color='grey')
    dmap.drawmapboundary()
def get_roms_url(time,method):
    '''
    use time to get roms url.     
    time is datetime.
    method is forecast or hindcast. 
    if method=='forecast':
        time is datetime
    if method=='hindcast':
        time is [datetime0,datetime1]
    '''
    if method=='forecast':
        date=time-dt.timedelta(days=3)
        str_date=dt.datetime.strftime(date.date(),"%Y-%m-%d")
        url='http://tds.marine.rutgers.edu:8080/thredds/dodsC/roms/espresso/2013_da/his/runs/ESPRESSO_Real-Time_v2_History_RUN_'+str_date+'T00:00:00Z'
    if method=='hindcast':
        if time<dt.datetime(2013,5,18,0,0,0):
            url='http://tds.marine.rutgers.edu:8080/thredds/dodsC/roms/espresso/2009_da/his'
        if time>=dt.datetime(2013,5,18,0,0,0):
            str_date=dt.datetime.strftime(time,"%Y%m%d")
            url='http://tds.marine.rutgers.edu:8080/thredds/dodsC/roms/espresso/2013_da/his/files/espresso_his_'+str_date+'_0000_0001.nc'
    return url    
def contour_fvcom_forecast(method,layer):
    'contour massbay temperature in recently 3 days in given layer''
    url="http://www.smast.umassd.edu:8080/thredds/dodsC/FVCOM/NECOFS/Forecasts/NECOFS_FVCOM_OCEAN_MASSBAY_FORECAST.nc"
    nc = netCDF4.Dataset(url)
    lat = nc.variables['lat'][:]
    lon = nc.variables['lon'][:]
    temp=nc.variables['temp']
    nv = nc.variables['nv'][:].T - 1 # read connectivity array
    time = nc.variables['time'][:]
    latsize=[min(lat)-0.1,max(lat)+0.1]
    lonsize=[min(lon)-0.1,max(lon)+0.1]   #set range you want to plot
    tri = Tri.Triangulation(lon,lat, triangles=nv)# create a triangulation object, specifying the triangle connectivity array
    levels=np.arange(1,30,0.1) #colorbar range
    if method=="mp4":
        #plot a mp4
        fig,ax=plt.subplots()
        draw_basemap(fig, ax, lonsize, latsize)
        def animate(i):
            del ax.lines[:]
            temprature=temp[3*i,int(layer),]
            temprature=np.array(temprature)
            TIME=dt.datetime(1858,11,17,0,0,0)+dt.timedelta(days=float(time[3*i])) #change time to datetime
            tri_temp=tricontourf(tri,temprature,levels=levels)
            plt.title('Temperature model, Time:'+str(TIME)[5:16],fontsize=30)
        anim = animation.FuncAnimation(fig, animate, frames=48)    
        anim.save('massbay_temperature.mp4',writer='mencoder',fps=2)
    if method=='gif':
        #plot a gif
        for i in range(48):  #legnth of time is 114,48 is every 3 hours. 
            fig,ax=plt.subplots()
            draw_basemap(fig, ax, lonsize, latsize)
            temprature=temp[3*i,int(layer),]
            temprature=np.array(temprature)
            TIME=dt.datetime(1858,11,17,0,0,0)+dt.timedelta(days=float(time[3*i])) #change time to datetime 
            tri_temp=tricontourf(tri,temprature,levels=levels)
            plt.title('Temperature model, Time:'+str(TIME)[5:16],fontsize=30)
            cbar=colorbar(ticks=[1,5,9,13,17,21,25,29])
            cbar.ax.tick_params(labelsize=20) 
            if i<10:
                plt.savefig('MASSBAY_temperature_00'+str(i)+'.png')  #save pic as 00X.png
            elif i<100:
                plt.savefig('MASSBAY_temperature_0'+str(i)+'.png')  #save pic as 0XX.png
            else:
                plt.savefig('MASSBAY_temperature_'+str(i)+'.png')  #save pic as XXX.png
        cmd='convert -delay 40 -loop 0 MASSBAY_temperature_*.png massbay_temperature.gif' 
        os.system(cmd)              #convert png to gif
def contour_roms_forecast(method,layer): 
    'contour roms temperature in recently 6 days in given layer'
    url=get_roms_url(dt.datetime.now(),'forecast')
    nc = netCDF4.Dataset(url)
    lat = nc.variables['lat_rho'][:]
    lon = nc.variables['lon_rho'][:]
    temp=nc.variables['temp']
    s_rho=nc.variables['s_rho']
    time = nc.variables['time'][:]
    latsize=[np.amin(lat),np.amax(lat)]
    lonsize=[np.amin(lon),np.amax(lon)]   #set range you want to plot
    LON,LAT=[],[]
    for i in range(len(lon)):
        for j in range(len(lon[i])):
            LON.append(lon[i][j])
            LAT.append(lat[i][j])
    lon_i = np.linspace(lonsize[0],lonsize[1],1000)
    lat_i = np.linspace(latsize[0],latsize[1],1000)     #use for mean error,absolute mean error and rms
    if method=="mp4":
        #plot a mp4
        fig,ax=plt.subplots()
        draw_basemap(fig, ax, lonsize, latsize)
        def animate(i):
            del ax.lines[:]
            temperature=temp[3*i,int(layer),:,:]
            temperature=np.array(temperature)
            T=[]
            for s in range(len(temperature)):
                for j in range(len(temperature[s])):
                    T.append(temperature[s][j])
            TIME=dt.datetime(2013,5,18,0,0,0)+dt.timedelta(hours=float(time[3*i])) #change time to datetime
            temp_i = griddata(np.array(LON),np.array(LAT),np.array(T),lon_i,lat_i,interp='linear')
            plt.contourf(lon_i, lat_i, temp_i,np.arange(0,30,0.1), cmap=plt.cm.rainbow,vmax=30, vmin=0)
            plt.title('Temperature model, Time:'+str(TIME)[5:16],fontsize=20)
        anim = animation.FuncAnimation(fig, animate, frames=53)    
        anim.save('roms_temperature.mp4',writer='mencoder',fps=2)
    if method=='gif':
        #plot a gif
        for i in range(53):  #length of time is 156,53 want every 3 hours. 
            fig,ax=plt.subplots()
            draw_basemap(fig, ax, lonsize, latsize)
            temperature=temp[3*i,int(layer),:,:]
            temperature=np.array(temperature)
            T=[]
            for s in range(len(temperature)):
                for j in range(len(temperature[s])):
                    T.append(temperature[s][j])
            TIME=dt.datetime(2013,5,18,0,0,0)+dt.timedelta(hours=float(time[3*i])) #change time to datetime 
            temp_i = griddata(np.array(LON),np.array(LAT),np.array(T),lon_i,lat_i,interp='linear')
            cs=plt.contourf(lon_i, lat_i, temp_i,np.arange(0,30,0.1), cmap=plt.cm.rainbow,vmax=30, vmin=0)
            plt.title('Temperature model, Time:'+str(TIME)[5:16],fontsize=20)
            cbar=colorbar(cs)
            cbar.ax.tick_params(labelsize=20) 
            if i<10:
                plt.savefig('ROMS_temperature_00'+str(i)+'.png')  #save pic as 00X.png
            elif i<100:
                plt.savefig('ROMS_temperature_0'+str(i)+'.png')  #save pic as 0XX.png
            else:
                plt.savefig('ROMS_temperature_'+str(i)+'.png')  #save pic as XXX.png  
        cmd='convert -delay 40 -loop 0 ROMS_temperature_*.png ROMS_temperature.gif' 
        os.system(cmd)              #convert png to gif
def contour_fvcom_hindcast(depth,TIME): 
    '''
    plot fvcom temperature in given time and depth.
    depth is negivate number
    TIME is datetime
    '''
    stime=dt.datetime.strptime(TIME, "%Y-%m-%d %H:%M:%S")
    timesnum=stime.year-1981
    standardtime=dt.datetime.strptime(str(stime.year)+'-01-01 00:00:00', "%Y-%m-%d %H:%M:%S")
    timedeltaprocess=(stime-standardtime).days
    startrecord=26340+35112*(timesnum/4)+8772*(timesnum%4)+1+timedeltaprocess*24 
    url="http://www.smast.umassd.edu:8080/thredds/dodsC/fvcom/hindcasts/30yr_gom3"
    nc = netCDF4.Dataset(url)
    lat = nc.variables['lat'][:]
    lon = nc.variables['lon'][:]
    temp=nc.variables['temp']
    sali=nc.variables["salinity"]
    siglay=nc.variables['siglay']
    h = nc.variables['h'][:]# read connectivity array
    nv = nc.variables['nv'][:].T - 1
    time_var = nc.variables['time']
    # create a triangulation object, specifying the triangle connectivity array
    tri = Tri.Triangulation(lon,lat, triangles=nv)
    # plot depth using tricontourf
    salinity=[]
    temprature=[]
    for i in range(len(lon)):  #get temperature and salinity in given depth
        depthtotal=siglay[:,i]*h[i]
        layer=np.argmin(abs(depthtotal+float(depth)))
        temprature.append(temp[int(startrecord),layer,i])
        salinity.append(sali[int(startrecord),layer,i])
    temprature=np.array(temprature)
    salinity=np.array(salinity)
    latsize=[min(lat)-0.1,max(lat)+0.1]
    lonsize=[min(lon)-0.1,max(lon)+0.1] #basemap range
    fig=figure(figsize=(12,16))
    ax=fig.add_subplot(111)
    draw_basemap(fig, ax, lonsize, latsize)
    levels=np.arange(np.amin(temprature),np.amax(temprature),0.1)
    tri_temp=tricontourf(tri,temprature,levels=levels)
    colorbar(tri_temp)
    plt.title('Temperature model,Depth:'+str(-depth)+'m, Time:'+str(TIME)[0:-9]) 
    plt.savefig('Temperature_fvcom.png')
    fig1=figure(figsize=(12,16))
    ax1=fig1.add_subplot(111)
    draw_basemap(fig1, ax1, lonsize, latsize)
    levels=np.arange(28,34,0.01)
    tri_sal=tricontourf(tri,salinity,levels=levels)
    colorbar()
    plt.title('Salinity model,Depth:'+str(-depth)+'m, Time:'+str(TIME)[0:-9]) 
    plt.savefig('Salinity_fvcom.png')
def contour_roms_hindcast(depth,TIME): 
    '''
    plot roms temperature in given time and depth.
    depth is negivate number
    TIME is datetime
    '''
    time_input=dt.datetime.strptime(TIME,"%Y-%m-%d %H:%M:%S") #change str to datetime 
    url=get_roms_url(time_input,'hindcast') #get url 
    nc = netCDF4.Dataset(url)
    lat = nc.variables['lat_rho'][:]
    lon = nc.variables['lon_rho'][:]
    s_rho=nc.variables['s_rho'][:]
    h = nc.variables['h'][:]
    time=nc.variables['ocean_time'][:]
    temp=nc.variables['temp']   #get data from web
    latsize=[np.amin(lat),np.amax(lat)]
    lonsize=[np.amin(lon),np.amax(lon)]   #set range you want to plot
    lon_i = np.linspace(lonsize[0],lonsize[1],1000)
    lat_i = np.linspace(latsize[0],latsize[1],1000)     #use for mean error,absolute mean error and rms
    Time=[]
    for i in range(len(time)):
        t=dt.datetime(2006,1,1,0,0,0)+dt.timedelta(seconds=time[i])
        Time.append(t)      #convert float to datetime
    nearest_time=np.argmin(abs(time_input-np.array(Time))) #find nearest time 
    LON,LAT,TEMP=[],[],[]
    for i in range(len(lon)):
        TEMP.append([])
        for j in range(len(lon[i])):
            LON.append(lon[i][j])
            LAT.append(lat[i][j])
            depth_total=s_rho*h[i][j]
            layer=np.argmin(abs(float(depth)-depth_total)) #find nearest layer in each node
            TEMP[i].append(temp[nearest_time,layer,i,j]) #get temperature in nearest layer in each node
    Temp=[]
    for i in range(len(TEMP)):
        for j in range(len(TEMP[i])):
            Temp.append(TEMP[i][j])   #use in griddata
    fig=plt.figure()
    ax=fig.add_subplot(111)
    draw_basemap(fig,ax,lonsize, latsize)
    temp_i = griddata(np.array(LON),np.array(LAT),np.array(Temp),lon_i,lat_i,interp='linear')
    cs=plt.contourf(lon_i, lat_i, temp_i,np.arange(min(Temp),max(Temp),0.1), cmap=plt.cm.rainbow,vmax=max(Temp), vmin=min(Temp))
    cbar=colorbar(ticks=[1,5,9,13,17,21,25,29])
    cbar.ax.tick_params(labelsize=20)
    plt.title('Temperature model, Time:'+str(Time[nearest_time])[0:16],fontsize=20) 
    plt.savefig('Temperature_roms.png')

