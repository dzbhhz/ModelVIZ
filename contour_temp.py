# -*- coding: utf-8 -*-
"""
Created on Tue Oct 13 12:31:19 2015
contour horizontal temperature 
@author: zdong
"""
from functions import contour_fvcom_forecast,contour_roms_forecast,contour_fvcom_hindcast,contour_roms_hindcast
import matplotlib.pyplot as plt
option1=input('hindcast or forecast:')   #for hindcast or forecast
option2=input('fvcom or roms or both:')    #which model you want
if option1=='hindcast':
    if option2=='fvcom':
        depth=input('please input depth you want(negivate number):')
        time=input('please input time you want("%Y-%m-%d %H:%M:%S"):')  #time and depth you want
        contour_fvcom_hindcast(depth,time)
    elif option2=='roms':
        depth=input('please input depth you want(negivate number):')
        time=input('please input time you want("%Y-%m-%d %H:%M:%S"):')  #time and depth you want
        contour_roms_hindcast(depth,time)
    elif option2=='both':
        depth=input('please input depth you want(negivate number):')
        time=input('please input time you want("%Y-%m-%d %H:%M:%S"):')  #time and depth you want
        contour_roms_hindcast(depth,time)
        contour_fvcom_hindcast(depth,time)
elif option1=='forecast':
    if option2=='fvcom':
        method=input('please input output style you want(gif or mp4):')         #output style
        layer_fvcom=input('please input fvcom layer you want(0~9,9 is bottom)')  #layer you want
        contour_fvcom_forecast(method,layer_fvcom)
    elif option2=='roms':
        method=input('please input output style you want(gif or mp4):')        #output style
        layer_roms=input('please input roms layer you want(0~35,0 is bottom)')  #layer you want
        contour_roms_forecast(method,layer_roms)
    elif option2=='both':
        method=input('please input output style you want(gif or mp4):')     #output style
        layer_roms=input('please input roms layer you want(0~35,0 is bottom)')  #layer you want
        layer_fvcom=input('please input fvcom layer you want(0~9,9 is bottom)')  #layer you want
        contour_roms_forecast(method,layer_roms)
        contour_fvcom_forecast(method,layer_fvcom)
plt.show()
