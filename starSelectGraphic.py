#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This program selects valid RR Lyrae stars for observation on a given night
and displays their altitude vs time graph with astronomical twilight region
and time of maxima graphed as well.

Note: Some stars do not have an epoch listed in GCVS and will break this

Created on Fri Feb 12 17:38:24 2021

@author: Kevin Connors
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from astropy.visualization import astropy_mpl_style, quantity_support
from astropy.coordinates import SkyCoord, EarthLocation, AltAz
from astropy.time import Time
import astropy.units as u
from astroplan import Observer
from datetime import date

plt.style.use(astropy_mpl_style)
quantity_support()

# =============================================================================
# This code will enable the graphics backend QT5 to create plots that account 
# for screen resolution settings. (notes: matplotlib default figure.dpi = 100,
#    physical screen dpi for 1920x1080 is 166 and for 3840x2160 is 333)
#    using 0.8 factor gives figure of  132.8 dpi and 266.4, respectively
# Use the following to return to all matplotlib default settings:
#     plt.style.use('default')  # resets matplotlib default settings
# Credit to Dr. Fair of Grove City College for this code.
# =============================================================================
if plt.get_backend() == 'Qt5Agg':
    import sys
    from matplotlib.backends.qt_compat import QtWidgets
    qApp = QtWidgets.QApplication(sys.argv)
    plt.matplotlib.rcParams['figure.dpi'] = 0.8*qApp.desktop().physicalDpiX()
# =============================================================================

# Obtains the altitude of an object at a certian location and time
def checkAltitude(objSkyCoord, time, loc):
    objAzAlt = objSkyCoord.transform_to(AltAz(obstime = time,
                                           location = loc))
    return objAzAlt.alt

# Returns a list of times of maxima for a list of objects in a given time range
def findTimesOfMaxima(obj, startTime, stopTime):
    objName = obj[0]
    objPD = obj[1]
    objEP = obj[2]
    
    timesOfMax = []
    
    for i in range(0, len(objName)):  
        timesOfMax.append([])
        
        tempTime = float(objEP[i]) + 2400000.
        tempTimeAstropy = Time(objEP[i], format="jd")
        startTimeJD = float(startTime.jd)
        
        period = objPD[i]
        initialSkips = np.floor(((startTimeJD-1)-tempTime)/period)
        tempTime += initialSkips*period
        
        while tempTimeAstropy < stopTime:
            if tempTimeAstropy > startTime:
                timesOfMax[i].append(tempTimeAstropy)
            
            tempTime += period
            tempTimeAstropy = Time(tempTime, format="jd")
    return timesOfMax

def main():
    
    # Observatory Coordinates
    lat = 41.81250
    lng = -80.09361
    hgt = 400
    
    loc = EarthLocation(lat = lat*u.deg,
                      lon = lng*u.deg,
                      height = hgt*u.m)
    obs = Observer(location=loc, timezone="US/Eastern")
    
    filename = "./app/static/PVMS_RR_Lyrae_Candidates.csv"
    file = open(filename)
    df = pd.read_csv(file)
    file.close()
    objName = df['Name'].values.tolist()
    objRA = df['RA (deg)'].values.tolist()
    objDE = df['DE (deg)'].values.tolist()
    objPD = df['Period'].values.tolist()
    objEP = df['Epoch'].values.tolist()
    objCoord = SkyCoord(objRA, objDE, unit='deg')
    obj = [objName, objPD, objEP]
    
    today = str(date.today())
    midnightUTC = Time(today + " 23:59:59")
    startTime = obs.twilight_evening_nautical(midnightUTC)
    stopTime = obs.twilight_morning_nautical(midnightUTC)
    print("Start Time:", startTime.isot)
    print("Stop Time:", stopTime.isot)
    print()
    
    altPlot = []
    timPlot = []
    timesOfMax = findTimesOfMaxima(obj, startTime, stopTime)
    
    # Fill altPlot with empty lists to append points to
    for i in range(0, len(objName)):
        altPlot.append([])
    
    # Makes each individual altitude plot
    nSteps = 15
    tau = (stopTime - startTime) / nSteps
    
    for i in range(0, nSteps + 1):
        time = startTime + i*tau
        for j in range(0, len(objName)):
            altPlot[j].append(checkAltitude(objCoord[j], time, loc)/u.deg)
        timPlot.append(mdates.date2num(time.datetime))
    
    # Creates figure with altitude plots and informative lines
    figSize = int(np.ceil(np.sqrt(len(objName))))
    fig, axis = plt.subplots(figSize, figSize, figsize=(10,8))
    
    for i in range(figSize):
        for j in range(figSize):
            curObj = i*figSize + j
            if (curObj < len(objName)):
                # Set the title of each plot
                axis[i,j].set_title(objName[curObj], fontsize="12")
                
                # Displays horizontal altitude lines for ~0, 25, and 90 degrees
                axis[i,j].axhline(0, linewidth=1, color="black")
                axis[i,j].axhline(25, linewidth=1, color="black", linestyle='--')
                axis[i,j].axhline(90, linewidth=1, color="black")
                
                # Displays vertical line for each maximum and prints to console
                for k in range(len(timesOfMax[curObj])):
                    timeOfMax = mdates.date2num(timesOfMax[curObj][k].datetime)
                    print(objName[curObj], timesOfMax[curObj][k].isot)
                    axis[i,j].axvline(timeOfMax, color="dodgerblue")
                
                # Displayes altitude plot over the course of the night
                axis[i,j].plot(timPlot, altPlot[curObj], color='indigo', 
                               label='Altitude')
                axis[i,j].set_ylim(-2, 91)
            
            axis[i,j].axis('off')
    
    fig.suptitle("The Night of " + today, fontsize="15")
    fig.tight_layout()
    fig.subplots_adjust(wspace = 0.5, hspace = 1)
    plt.close(fig)
    fig.savefig("app/static/plot.png")
    return 1

if __name__ == "__main__":
    main()
