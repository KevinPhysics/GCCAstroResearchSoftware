#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This program generates a schedule file for a night of observations.

Created on Fri Sep 10 10:17:02 2021

@author: Kevin Connors
"""

from astropy import coordinates as coord
from exposureTimeCalculator import expose

def main():
    title = 'object'
    observer = 'Clem'
    source = 'CZ Lac'
    epoch = '2000'
    lststart = '14:00:00'
    mag = 10
    
    fileName = source + "_BVRIH.sch"
    ra,dec = coord.SkyCoord.from_name(source).to_string('hmsdms').split(' ')
    ra = ra[0:2] + ':' + ra[3:5] + ':' + str(round(float(ra[6:-1])))
    dec = dec[0:3] + ':' + dec[4:6] + ':' + str(round(float(dec[7:-1])))
    exposureTimes = [str(round(expose('B',mag))),
                     str(round(expose('V',mag))),
                     str(round(expose('R',mag))),
                     str(round(expose('I',mag))),
                     str(round(expose('H',mag)))]
    exposureTimes = ','.join(exposureTimes)
    
    inputs = [title, observer, source, ra, dec, epoch, lststart, exposureTimes]
    
    writeSchedule(fileName, inputs)

def writeSchedule(sch_file, inputs):
    title = inputs[0]
    observer = inputs[1]
    source = inputs[2]
    ra = inputs[3]
    dec = inputs[4]
    epoch = inputs[5]
    lststart = inputs[6]
    filters = inputs[7]
    duration = inputs[8]
    binning = inputs[9]
    subimage = inputs[10]
    priority = inputs[11]
    compress = inputs[12]
    imagedir = inputs[13]
    ccdcalib = inputs[14]
    shutter = inputs[15]
    repeat = inputs[16]
    
    with open(sch_file,'w') as schedule:
        schedule.write('TITLE    = \'' + title + '\'\n')
        schedule.write('OBSERVER = \'' + observer + '\'\n')
        schedule.write('SOURCE   = \'' + source + '\'\n')
        schedule.write('RA       = \'' + ra + '\'\n')
        schedule.write('DEC      = \'' + dec + '\'\n')
        schedule.write('EPOCH    = ' + epoch + '\n')
        schedule.write('LSTSTART = \'' + lststart + '\'\n')
        schedule.write('FILTER   = \'' + filters + '\'\n')
        schedule.write('DURATION = \'' + duration + '\'\n')
        schedule.write('BINNING  = \'' + binning + '\'\n')
        schedule.write('SUBIMAGE = \'' + subimage + '\'\n')
        schedule.write('PRIORITY = ' + priority + '\n')
        schedule.write('COMPRESS = ' + compress + '\n')
        schedule.write('IMAGEDIR = \'' + imagedir + '\'\n')
        schedule.write('CCDCALIB = \'' + ccdcalib + '\'\n')
        schedule.write('SHUTTER  = \'' + shutter + '\'\n')
        schedule.write('REPEAT   = ' + repeat + '\n')
        schedule.write('/\n')
        
def DDToDMS(dd):
    mnt,sec = divmod(dd*3600,60)
    deg,mnt = divmod(min,60)
    return deg,mnt,sec

if __name__ == '__main__':
    print(main.__doc__)
    main()