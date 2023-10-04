import os
import glob
from glob import glob
import pandas as pd
import geopandas as gpd
import rasterio
from rasterio.plot import show
from rasterstats import zonal_stats
import shutil
import math
import subprocess
from geojson import Polygon
from os.path import join, isdir, isfile
from datetime import datetime
from zipfile import ZipFile

# Set data paths
data_path = os.getenv('DATA','/data')

# Set up Data Input Paths
inputs_path = os.path.join(data_path, 'inputs')
boundary_path = os.path.join(inputs_path, 'boundary')
lads_path = os.path.join(inputs_path,'lads')
parameters_path = os.path.join(inputs_path,'parameters')
ssp_path = os.path.join(inputs_path,'ssp')

# Create the subfolder structure
inputs_urban_path=os.path.join(inputs_path,'urban_data')
if not os.path.exists(inputs_urban_path):
    os.mkdir(inputs_urban_path)
inputs_rural_path=os.path.join(inputs_path,'rural_data')
if not os.path.exists(inputs_rural_path):
    os.mkdir(inputs_rural_path)
inputs_total_path=os.path.join(inputs_path,'total_data')
if not os.path.exists(inputs_total_path):
    os.mkdir(inputs_total_path)


# Set up and create data output paths
outputs_path = os.path.join(data_path, 'outputs')
if not os.path.exists(outputs_path):
    os.mkdir(outputs_path)

# Define output path for parameters
parameters_out_path=os.path.join(outputs_path,'parameters')
if not os.path.exists(parameters_out_path):
    os.mkdir(parameters_out_path)

# Look to see if a parameter file has been added
parameter_file = glob(parameters_path + "/*.csv", recursive = True)
print('parameter_file:', parameter_file)

# Find out which ssp was used:
if len(parameter_file) != 0 :
    parameters = pd.read_csv(parameter_file[0])
    ssp = parameters.loc[1][1]

## To obtain the SSP data, we first need to unzip the global dataset and reallocate the ###
## urban, rural and total population rasters in appropriate folders ###
## This section of code identifies all files, moves them, and then deletes the parent folder ###
## inputs/ssps ###

# Identify the zip file
archive = glob(inputs_path + "/**/*.zip", recursive = True)

matches = []
for match in archive:
    if "downscaled" in match:
        matches.append(match)
check = []
if len(matches) == 1:
    with ZipFile(matches[0],'r') as zip:
        check = zip.namelist()
        #print('Check:',check)

# Unzip the files into the inputs/ssp directory
if len(check) != 0 :
    stop_code = 0
    if os.path.exists(matches[0]) :
        with ZipFile(matches[0], 'r') as zip: 
            # extract the files into the ssp directory
            zip.extractall(ssp_path)



### All of the global datasets need to be cropped to the shape of the country outline ###
### This section will locate the boundary file, and clip all tiff files and move them to the inputs/ssp folder ###

boundary = glob(boundary_path + "/*.*", recursive = True)
rasters = glob(ssp_path + "/**/*.tif", recursive = True)

raster_output_clip =[]
raster_output_clip=['xx' for n in range(len(rasters))]
print(raster_output_clip)

filename=[]
filename=['xx' for n in range(len(rasters))]

#Create a list of all of the files in the folder
for i in range(0,len(rasters)):
    test = rasters[i]
    file_path = os.path.splitext(test)
    filename[i]=file_path[0].split("/")
    raster_output_clip[i]=os.path.join(ssp_path,filename[i][-1]+'_clip.tif')
print('raster_output_clip:',raster_output_clip)

for i in range(0,len(raster_output_clip)):
    # Crop the raster to the polygon shapefile
    command_output = subprocess.run(["gdalwarp", "-cutline", boundary[0], "-crop_to_cutline", rasters[i],
                        raster_output_clip[i], '-dstnodata', '-9999'])



### Now the datasets have been cropped, we want to move them into the correct folders ###
### Those relating to land use change need to go into the inputs/rural_data and inputs/ ###
### urban_data, whilst the population data needs to go into the inputs/total_data folder ###


# Once the files have been unzipped, create a list of all files ready to be moved.
archive2 = glob(ssp_path + "/*.tif", recursive = True)

filename=[]
filename=['xx' for n in range(len(archive2))]

# Create a list of all of the files in the folder
for i in range(0,len(archive2)):
    test = archive2[i]
    file_path = os.path.splitext(test)
    filename[i]=file_path[0].split("/")[-1]+'.tif'


print('filename:', filename)

file =[]
# Identify which files related to rural land use change and move them into the /inputs/rural_data path
for i in range(0,len(archive2)):
    if 'rural' in filename[i]:
        file = archive2[i]
        dst = os.path.join(inputs_rural_path, filename[i])
        src=file
        shutil.move(src,dst)

# Identify which files related to population change and move them into the /inputs/total_data path  
for i in range(0,len(archive2)):
    if 'total' in filename[i]:
        file = archive2[i]
        dst = os.path.join(inputs_total_path, filename[i])
        src=file
        shutil.move(src,dst)

# Identify which files related to urban land use change and move them into the /inputs/urban_data path    
for i in range(0,len(archive2)):
    if 'urban' in filename[i]:
        file = archive2[i]
        dst = os.path.join(inputs_urban_path, filename[i])
        src=file
        shutil.move(src,dst)

# # Finally delete the inputs/ssp folder to create space and save storing unused data
# shutil.rmtree(ssp_path)

total = glob(os.path.join(inputs_total_path, '*.tif'))
rural = glob(os.path.join(inputs_rural_path, '*.tif'))
urban = glob(os.path.join(inputs_urban_path, '*.tif'))


lads = glob(os.path.join(lads_path, '*.gpkg'))
print(lads)


stats = []
stats = pd.DataFrame()

for i in range(0,len(total)):
    test = total[i]
    file_path = os.path.splitext(test)
    filename=file_path[0].split("/")
    unit_name = filename[-1]
    dem = rasterio.open(total[i])
    array = dem.read(1)
    array[array < 0] = 0
    affine = dem.transform
    stats[i]= zonal_stats(lads[0], array, affine=affine, stats=['sum'])
    for j in range(0,len(stats[i])):
        stats[i][j]=str(stats[i][j])
        remove_string=stats[i][j].split(':')
        stats[i][j] = remove_string[-1]
        remove_string_2=stats[i][j].split('}')
        stats[i][j] = remove_string_2[0]
    if i ==0:
        sum = pd.DataFrame({unit_name:stats[i].astype(float)})
    else:
        new = pd.DataFrame({unit_name:stats[i].astype(float)})
        sum = sum.join(new)

poly = gpd.read_file(lads[0])
poly = poly.join(sum)
total_result = os.path.join(outputs_path,'total_population_'+ssp+'.gpkg')
poly.to_file(total_result, driver='GPKG')


stats = []
stats = pd.DataFrame()

for i in range(0,len(urban)):
    test = urban[i]
    file_path = os.path.splitext(test)
    filename=file_path[0].split("/")
    unit_name = filename[-1]
    dem = rasterio.open(urban[i])
    array = dem.read(1)
    array[array < 0] = 0
    affine = dem.transform
    stats[i]= zonal_stats(lads[0], array, affine=affine, stats=['sum'])
    for j in range(0,len(stats[i])):
        stats[i][j]=str(stats[i][j])
        remove_string=stats[i][j].split(':')
        stats[i][j] = remove_string[-1]
        remove_string_2=stats[i][j].split('}')
        stats[i][j] = remove_string_2[0]
    if i ==0:
        sum = pd.DataFrame({unit_name:stats[i].astype(float)})
    else:
        new = pd.DataFrame({unit_name:stats[i].astype(float)})
        sum = sum.join(new)

poly = gpd.read_file(lads[0])
poly = poly.join(sum)
urban_result = os.path.join(outputs_path,'urban_population_'+ssp+'.gpkg')
poly.to_file(urban_result, driver='GPKG')


stats = []
stats = pd.DataFrame()

filename=[]
filename = pd.DataFrame()

for i in range(0,len(rural)):
    test = rural[i]
    file_path = os.path.splitext(test)
    filename=file_path[0].split("/")
    unit_name = filename[-1]
    dem = rasterio.open(rural[i])
    array = dem.read(1)
    array[array < 0] = 0
    affine = dem.transform
    stats[i]= zonal_stats(lads[0], array, affine=affine, stats=['sum'])
    for j in range(0,len(stats[i])):
        stats[i][j]=str(stats[i][j])
        remove_string=stats[i][j].split(':')
        stats[i][j] = remove_string[-1]
        remove_string_2=stats[i][j].split('}')
        stats[i][j] = remove_string_2[0]
    if i ==0:
        sum = pd.DataFrame({unit_name:stats[i].astype(float)})
    else:
        new = pd.DataFrame({unit_name:stats[i].astype(float)})
        sum = sum.join(new)

poly = gpd.read_file(lads[0])
poly = poly.join(sum)
rural_result = os.path.join(outputs_path,'rural_population_'+ssp+'.gpkg')
poly.to_file(rural_result, driver='GPKG')



### For information flow, the parameter file created in the inputs model should be carried forward ###

# Search for a parameter file which outline the input parameters defined by the user
parameter_file = glob(parameters_path + "/*.csv", recursive = True)


filename=[]
filename=['xx' for n in range(len(parameter_file))]
# Move the parameter file into the outputs/parameters folder
if len(parameter_file) == 1 :
    file_path = os.path.splitext(parameter_file[0])
    filename=file_path[0].split("/")

    src = parameter_file[0]
    dst = os.path.join(parameters_out_path,filename[-1] + '.csv')
    shutil.copy(src,dst)
