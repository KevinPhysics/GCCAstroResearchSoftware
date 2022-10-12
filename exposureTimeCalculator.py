#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This program generates exposure times for a given filter and a star with a
given magnitude.

Created on Thu Mar 18 11:18:46 2021

@author: Keith Dabroski
"""

import numpy as np
from numba import jit
from sympy import symbols, solve

def extinction(Filter):
    """
    Method to calculate extinction coefficent based on filter
    Filter: U, B, V, R, or I
    Returns extinction coefficient, -1.0 if invalid filter
    """
    
    if Filter == 'U':
        coef = 0.6
    elif Filter == 'B':
        coef = 0.4
    elif Filter == 'V':
        coef = 0.2
    elif Filter == 'R':
        coef = 0.1
    elif Filter == 'I':
        coef = 0.08
    elif Filter == 'H':
        coef = 0.1
    else:
        coef = -1.0
    return coef

def mag_zeropoint(Filter):
    """
    Given a filter, return the number of photons per cm^2 per s
    of a star with 0 magnitude above the atmosphere.
    Assume spectrum like Vega
    """
    
    if Filter == 'U':
        nPhot = 5.5e5
    elif Filter == 'B':
        nPhot = 3.91e5
    elif Filter == 'V':
        nPhot = 8.66e5
    elif Filter == 'R':
        nPhot = 1.1e6
    elif Filter == 'I':
        nPhot = 6.75e5
    elif Filter == 'H':
        nPhot = 9.83e5
    else:
        nPhot = -1.0
    return nPhot

def get_qe(Filter):
    """
    Given a filter, return the quantum efficiency at the filter's central wavelength
    """
    
    if Filter == 'U':
        qe =  0.28
    elif Filter == 'B':
        qe = 0.45
    elif Filter == 'V':
        qe = 0.65
    elif Filter == 'R':
        qe = 0.6
    elif Filter == 'I':
        qe = 0.48
    elif Filter == 'H':
        qe = 0.58
    else:
        qe = -1.0
    return qe

@jit(nopython=True, cache=False)
def fraction_inside_slow(FWHM,radius,pixSize):
    """
    Figure out what fraction of a star's light falls within the aperture.
    Assumes that the starlight has a circular gaussian distribution.
    This function goes to the trouble of calculating how much of the light
    falls within fractional pixels defined by the given radius of a synthetic
    aperature.  It is slow, but more accurate than the "fraction_inside" function.
    recieves:
        FWHM     -  Full Width Half Max (arcsec)
        radius   -  radius of aperture (arcsec)
        pixSize  -  size of pixel  (arcsec)
    return:
        ratio    -  fraction of star's light within aperture
    """
    
    piece = 20 # Pieces to sub-divide pixels into
    
    # Rescale FWHM and aperture radius into pixels
    FWHM /= pixSize
    radius /= pixSize
    
    max_pix_rad = 30
    
    # place the star on the pixel grid
    psf_center_x = 0.5
    psf_center_y = 0.5
    
    sigma2 = (FWHM/2.35)**2
    radius2 = radius**2
    bit = 1.0/piece
    
    rad_sum = 0.0
    all_sum = 0.0
    
    for i in range(-max_pix_rad,max_pix_rad):
        for j in range(-max_pix_rad,max_pix_rad):
            pix_sum = 0.0
            for k in range(0,piece):
                x = i - psf_center_x + (k + 0.5)*bit
                fx = np.exp(-(x*x)/(2.0*sigma2))
                
                for l in range(0,piece):
                    y = j - psf_center_y + (l + 0.5)*bit
                    fy = np.exp(-(y*y)/(2.0*sigma2))
                    inten = fx*fy
                    this_bit = inten*bit*bit
                    pix_sum += this_bit
                    
                    rad2 = x*x + y*y
                    if(rad2 <= radius2):
                        rad_sum += this_bit
            all_sum += pix_sum
    ratio = rad_sum / all_sum
    return ratio


def expose(Filter,mag):
    """
    Calculates the desired exposure time
    Recieves:
        Filter  -  The filter
        mag     -  The magnitude of the star
    
    Returns:
        The exposure Time in seconds
    """
    tel_diam = 50.0             # Telescope diameter (cm)
    qe = get_qe(Filter)         # Overall QE of CCD (0 - 1.0)
    readNoise = 15.78           # Read Noise of CCD (electrons)
    pixSize = 0.442             # Pixel size of CCD (arcsec/pixel)
    sky = 19.0                  # Sky brightness (mag/arcsec^2)
    airmass = 1.77              # Airmass of object
    SNR = 1000.0                 # Desired signal to noise ratio
    FWHM = 2.5                  # Full width half max of object (arcsec)
    aper_rad = 8.0*pixSize      # Area over with signal is measured (arcsec)
    
    # Get the extinction coefficient appropriate for filter
    extinct_coeff = extinction(Filter)
    
    # Get the number of photons from a mag-zero star per sq cm per sec
    nphoton = mag_zeropoint(Filter)
    
    # Number of pixels inside aperture
    npix = (np.pi*aper_rad*aper_rad)/(pixSize*pixSize)
    
    # Fraction of star's light in aperture
    fraction = fraction_inside_slow(FWHM, aper_rad, pixSize)
    
    
    # Calculate the number of electrons collected on the CCD from star in total per second
    x = np.power(10.0,-0.4*mag)*nphoton
    x *= np.pi*tel_diam*tel_diam*0.25
    x *= qe
    star_electrons = x
    
    # Decrease the number of electrons per second from star due to extinction
    x = airmass*extinct_coeff
    star_electrons *= np.power(10.0,-0.4*x)
    
    # Calculate the number of electrons collected on the CCD from sky per pixel per second
    x = np.power(10.0,-0.4*sky)*nphoton
    x *= np.pi*tel_diam*tel_diam*0.25
    x *= qe
    x *= pixSize*pixSize
    sky_electrons_per_pix = x
    
    # Total number of electrons per second from star inside aperture
    star_electrons *= fraction
    
    # Total number of electrons from sky inside aperture per second
    sky_electrons = sky_electrons_per_pix*npix
    
    # Total number of electrons from readout in aperture
    read_electrons = readNoise*readNoise*npix
    
    # Solve signal to noise equation for exposure time
    t = symbols('t')
    expr = SNR - ((star_electrons*t)/
    ((read_electrons + sky_electrons*t + star_electrons*t)**0.5))
    
    # Return the exposure time in seconds
    return solve(expr)[0]

def main():
    """
    Program to calculate the ideal exposure time for a given filter and
    """
    mag = 10
    print("U:",expose('U',mag))
    print("B:",expose('B',mag))
    print("V:",expose('V',mag))
    print("R:",expose('R',mag))
    print("I:",expose('I',mag))
    print("H:",expose('H',mag))

if __name__ == '__main__':
    print(main.__doc__)
    main()