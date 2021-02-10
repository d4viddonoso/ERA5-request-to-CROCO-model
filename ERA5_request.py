#!/usr/bin/env python

# Script to download ECMWF ERA5 reanalysis datasets from the Climate Data
#  Store (CDS) of Copernicus https://cds.climate.copernicus.eu
#
#  This script use the CDS Phyton API[*] to connect and download specific ERA5 
#  variables, for a chosen area and monthly date interval, required by CROCO to 
#  perform simulations with atmospheric forcing. Furthermore, this script use 
#  ERA5 parameter names and not parameter IDs as these did not result in stable 
#  downloads. 
#
#  Tested using Python 3.8.6. This script need the following python libraries 
#  pre-installed: "datetime", "calendar", "os" and "json".
#
#  [*] https://cds.climate.copernicus.eu/api-how-to
#
#  Copyright (c) DDONOSO February 2021
#  e-mail:ddonoso@dgeo.udec.cl  
#

#  You may see all available ERA5 variables at the following website
#  https://confluence.ecmwf.int/display/CKB/ERA5%3A+data+documentation#ERA5:datadocumentation-Parameterlistings


# *******************************************************************************
#                         U S E R  *  O P T I O N S
# *******************************************************************************
# Dates limits
year_start = 2020
month_start = 11
year_end = 2020
month_end = 12

# Overlapping days (at the beginning/end of each month)
n_overlap = 1

# Request time (daily hours '00/01/.../23')
time = '00/01/02/03/04/05/06/07/08/09/10/11/12/13/14/15/16/17/18/19/20/21/22/23'

# Request area ([north, west, south, east])
varea = [-30, -80, -40, -70]

# Request variables (see availables at ERA5_variables.json)
variables = ['meets','mntss','msnswrf','msnlwrf','msshf','mslhf','mer','mtpr', \
             'sst','t2m','d2m','q','msl','u10','v10']


# -------------------------------------------------
# Getting libraries and utilities
# -------------------------------------------------
import cdsapi
from ERA5_utilities import *
import datetime
import calendar
import os
import json
import cdsapi


# -------------------------------------------------
# Setting output directory
# -------------------------------------------------
# Get the current directory
main_dir = os.getcwd()

# Output directory
era5_dir = main_dir + '/ERA5'

# Making output directory 
os.makedirs(era5_dir,exist_ok=True)


# -------------------------------------------------
# Loading ERA5 variables's information as 
# python Dictionary from JSON file
# -------------------------------------------------
with open('ERA5_variables.json', 'r') as jf:
    era5 = json.load(jf)


# -------------------------------------------------
# Downloading ERA5 datasets
# -------------------------------------------------
# Monthly dates limits
monthly_date_start = datetime.datetime(year_start,month_start,1)
monthly_date_end = datetime.datetime(year_end,month_end,1)

# Length of monthly dates loop
len_monthly_dates = (monthly_date_end.year - monthly_date_start.year) * 12 + \
                    (monthly_date_end.month - monthly_date_start.month) + 1

# Initial monthly date
monthly_date = monthly_date_start

# Monthly dates loop
for j in range(len_monthly_dates):

    # Year and month
    year = monthly_date.year;
    month = monthly_date.month;

    # Number of days in month
    days_in_month = calendar.monthrange(year,month)[1]

    # Date limits
    date_start = datetime.datetime(year,month,1)
    date_end = datetime.datetime(year,month,days_in_month)

    # Ordinal date limits (days)
    n_start = datetime.date.toordinal(date_start)
    n_end = datetime.date.toordinal(date_end)

    # Overlapping date string limits (yyyy-mm-dd)
    datestr_start_overlap = datetime.date.fromordinal(n_start - n_overlap).strftime('%Y-%m-%d')
    datestr_end_overlap = datetime.date.fromordinal(n_end + n_overlap).strftime('%Y-%m-%d')

    # Overlapping date string interval 
    vdate = datestr_start_overlap + '/' + datestr_end_overlap

    # Variables/Parameters loop
    for k in range(len(variables)):

        # Variable's name, long-name and level-type
        vname = variables[k]
        vlong = era5[vname][0]
        vlevt = era5[vname][3]

        # Request options
        options = {
             'product_type': 'reanalysis',
             'type': 'an',
             'date': vdate,
             'variable': vlong,
             'levtype': vlevt,
             'area': varea,
             'format': 'netcdf',
                  }

        # Add options to Variable without "diurnal variations"
        if vlong == 'sea_surface_temperature':
           options['time'] = '12'
   
        else:
           options['time'] = time

        # Add options to Product "pressure-levels"
        if vlong == 'specific_humidity' or vlong == 'relative_humidity':
           options['pressure_level'] = '1000'
           product = 'reanalysis-era5-pressure-levels'

        # Product "single-levels"
        else:
           product = 'reanalysis-era5-single-levels'

        # Output filename
        fname = 'ERA5_ecmwf_' + vname.upper() + '_Y' + str(year) + 'M' +  str(month).zfill(2) +'.nc'
        output = era5_dir + '/' + fname

        # Information strings
        info_time_clock = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        info_mdate = datetime.date(year,month,1).strftime('%Y-%b')
        info_n_overlap = ' with ' + str(n_overlap) + ' overlapping day(s) '

        # Printing message on screen
        print('                                                           ')
        print('-----------------------------------------------------------')
        print('',info_time_clock,'                                        ')
        print(' Performing ERA5 data request, please wait...              ')
        print(' Date [yyyy-mmm] =',info_mdate + info_n_overlap             )
        print(' Variable =',vlong,'                                       ')
        print('-----------------------------------------------------------')

        # Server ECMWF-API
        c = cdsapi.Client()

        # Do the request
        c.retrieve(product,options,output)
  
    # ---------------------------------------------------------------------
    # Next iteration to monthly date: add one month to current monthly date
    # ---------------------------------------------------------------------
    monthly_date = addmonths4date(monthly_date,1)


# Print output message on screen
print('                                               ')
print(' ERA5 data request has been done successfully! ')
print('                                               ')




