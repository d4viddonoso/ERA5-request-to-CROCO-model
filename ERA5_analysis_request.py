#!/usr/bin/env python

# Script to perform ERA5 analysis request
#  This file is (would like to be) part of CROCOTOOLS
#
#  The following variables are needed to make...
#
#  ------------------------------------------------
#  FORCING
#  ------------------------------------------------
#  - "mean_eastward_turbulent_surface_stress"
#  - "mean_northward_turbulent_surface_stress" 
#  - "mean_surface_net_short_wave_radiation_flux"
#  - "mean_surface_net_long_wave_radiation_flux"
#  - "mean_evaporation_rate"
#  - "mean_total_precipitation_rate"
#  - "sea_surface_temperature"
#  - "2m_temperature"
#  - "2m_dewpoint_temperature"
#  - "specific_humidity"
#  - "mean_sea_level_pressure"
#  - "10m_u_component_of_wind"
#  - "10m_v_component_of_wind"
#
#  ------------------------------------------------
#  BULK
#  ------------------------------------------------
#  - "2m_temperature"
#  - "specific_humidity"
#  - "relative_humidity"
#  - "mean_sea_level_pressure"
#  - "10m_u_component_of_wind"
#  - "10m_v_component_of_wind"
#  - "mean_total_precipitation_rate"
#  - "mean_surface_net_short_wave_radiation_flux"
#  - "mean_surface_net_long_wave_radiation_flux"
# 
#  This script has been tested using Python 3.8.6 and
#  it need the modules: "cdsapi"[*], "datetime", 
#  "calendar", "os" and "json".
#
#  [*] https://cds.climate.copernicus.eu/api/v2
#
#  Copyright (c) DDONOSO February 2020
#  e-mail:ddonoso@dgeo.udec.cl  
#


import cdsapi       
import datetime
import calendar
import os
import json


# *************************************************
#             U S E R  *  O P T I O N S
# *************************************************
# Dates limits
year_start = 2020
month_start = 12
year_end = 2021
month_end = 1

# Overlapping days (at the beginning/end of each month)
n_overlap = 1

# Request time (daily hours '00/01/.../23')
time = '00/01/02/03/04/05/06/07/08/09/10/11/12/13/14/15/16/17/18/19/20/21/22/23'
#time = '00/06/12/18'

# Request area ([north, west, south, east])
area = [-30, -80, -40, -70]

# Request variables (see all availables at "era5_variables.json")
variables = ['sea_surface_temperature', \
             '2m_temperature', \
             'specific_humidity']


# -------------------------------------------------
# Setting output directory
# -------------------------------------------------
# Get the current directory
main_dir = os.getcwd()

# Output directory
era5_dir = main_dir + '/ERA5_analysis'

# Making output directory 
os.makedirs(era5_dir,exist_ok=True)


# -------------------------------------------------
# Loading ERA5 variables's information as 
# python Dictionarry from JSON file
# (https://apps.ecmwf.int/codes/grib/param-db)
# -------------------------------------------------
with open('era5_variables.json', 'r') as jf:
    era5 = json.load(jf)


# -------------------------------------------------
# Function: Increment datetime by custom months
# (https://stackoverflow.com/questions/4130922/how-to-increment-datetime-by-custom-months-in-python-without-using-library)
# -------------------------------------------------
def add_months(sourcedate,months):
    month = sourcedate.month - 1 + months
    year = sourcedate.year + month // 12
    month = month % 12 + 1
    day = min(sourcedate.day,calendar.monthrange(year,month)[1])
    return datetime.date(year,month,day)


# -------------------------------------------------
# Downloading data
# -------------------------------------------------
# Monthly dates limits
mdate_start = datetime.datetime(year_start,month_start,1)
mdate_end = datetime.datetime(year_end,month_end,1)

# Length of monthly dates loop
len_mdates = (mdate_end.year - mdate_start.year) * 12 + (mdate_end.month - mdate_start.month) + 1

# Initial monthly date
mdate = mdate_start

# Monthly dates loop
for j in range(len_mdates):

    # Year and month
    year = mdate.year;
    month = mdate.month;

    # Days in month
    days_in_month = calendar.monthrange(year,month)[1]

    # Ordinal date limits (days)
    n_start =  datetime.date.toordinal(datetime.datetime(year,month,1))
    n_end =  datetime.date.toordinal(datetime.datetime(year,month,days_in_month))

    # Overlapping ordinal date limits (days)
    n_start_overlap = n_start - n_overlap
    n_end_overlap = n_end + n_overlap

    # Overlapping gregorian date limits (yyyy-mm-dd)
    date_start_overlap = datetime.date.fromordinal(n_start_overlap).strftime('%Y-%m-%d')
    date_end_overlap = datetime.date.fromordinal(n_end_overlap).strftime('%Y-%m-%d')

    # Request date (overlapping date interval)
    date = date_start_overlap + '/' + date_end_overlap

    # Variables/Parameters loop
    for k in range(len(variables)):

        # Variable's name, level-type and abbreviation
        vname = variables[k]
        vlevt = era5[vname][1]
        vabbr = era5[vname][2]

        # Request options
        options = {
             'product_type': 'reanalysis',
             'type': 'an',
             'date': date,
             'variable': vname,
             'levtype': vlevt,
             'area': area,
             'format': 'netcdf',
                  }

        # Add options to Variable without "diurnal variations"
        if vname == 'sea_surface_temperature':
           options['time'] = '12'
   
        else:
           options['time'] = time

        # Add options to Product "pressure-levels"
        if vname == 'specific_humidity' or vname == 'relative_humidity':
           options['pressure_level'] = '1000'
           product = 'reanalysis-era5-pressure-levels'

        # Product "single-levels"
        else:
           product = 'reanalysis-era5-single-levels'

        # Output filename
        fname = 'ERA5_ecmwf_' + vabbr + '_Y' + str(year) + 'M' +  str(month).zfill(2) +'.nc'
        output = era5_dir + '/' + fname

        # Information strings
        info_time_clock = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        info_mdate = datetime.date(year,month,1).strftime('%Y-%b')
        info_n_overlap = ' with ' + str(n_overlap) + ' overlapping day(s) '

        # Printing message on screen
        print('                                                           ')
        print('-----------------------------------------------------------')
        print('',info_time_clock,'                                        ')
        print(' Performing ERA5 analysis request, please wait...          ')
        print(' Date [yyyy-mmm] =',info_mdate + info_n_overlap             )
        print(' Variable =',vname,'                                       ')
        print('-----------------------------------------------------------')

        # Server ECMWF-API
        c = cdsapi.Client()

        # Do the request
        c.retrieve(product,options,output)
  
    # -------------------------------------------------------------------
    # Next iteration monthly date: add one month to current monthly date
    # -------------------------------------------------------------------
    mdate = add_months(mdate,1)


# Print output message on screen
print('                                          ')
print(' ERA5 request has been done successfully! ')
print('                                          ')




