#!/usr/bin/env python
# coding: utf-8

# # Extraction from list of irregular spaced points to other irregular spaced point list
# 
#     Output: list of points (irregular spaced) and values, user specified crs
#     Input: list of values with point locations (either json or csv)
#     Operations needed:
#         interpolation/traingulation between point coordinates
#         crs conversion
# 

# In[46]:


import geopandas as gpd
import numpy as np
from scipy.interpolate import griddata
import matplotlib.pyplot as plt


# In[14]:


filename = "../data/Griddata_cropped_Llara.csv"
gdf = gpd.read_file(filename)
gdf


#A function for making some synthetic data point data within the bounds
def create_points(n=100,lonmin=-180,lonmax=180,latmin=-90,latmax=90):
    lons = np.random.uniform(lonmin, lonmax, size=n)
    lats = np.random.uniform(latmin, latmax, size=n)
    pairs = np.c_[lons,lats]
    return(pairs)


#Make the random synthetic points
qarray=create_points(1000,float(gdf.Longitude.min()),float(gdf.Longitude.max()),
                                                          float(gdf.Latitude.min()),float(gdf.Latitude.max()))


#Zip up the lat/lon pairs for interploation
pointsarr=np.c_[gdf.Longitude.astype('float'),gdf.Latitude.astype('float')]

#Find the values of the isynthetic points nterpolated off the known points
newarr=scipy.interpolate.griddata(pointsarr, gdf.field_1, qarray, method='linear', fill_value=np.nan, rescale=False)



#plot it to make sure it looks right
fig = plt.figure(figsize=(10,10))

plt.scatter(gdf.Longitude.astype('float'),gdf.Latitude.astype('float'),c=gdf.field_1.astype('float'))

plt.scatter(qarray[:,0],qarray[:,1],c=newarr,s=10,marker='s',edgecolors='k')






