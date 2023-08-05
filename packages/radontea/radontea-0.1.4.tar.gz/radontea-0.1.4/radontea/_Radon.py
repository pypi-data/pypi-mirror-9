#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    _Radon.py
    
    Performs the radon transform.
"""
from __future__ import division
from __future__ import print_function

import numpy as np
import os
import scipy
import scipy.ndimage

import warnings

__all__ = ["radon", "radon_fan_translation", "get_fan_coords",
           "get_det_coords"]



def get_det_coords(size, spacing):
    """ Compute pixel-center positions for 2d detector
    
    The centers of the pixels of a detector are usually not aligned to
    a pixel grid. If we center the detector at the origin, odd images
    will have a pixel at zero, whereas even images will have two pixels
    next to the actual center.
    
    Parameters
    ----------
    size : int
        Size of the detector (number of detection points).
    spacing : float
        Distance between two detection points in pixels.
        
    Returns
    -------
    arr : 1D ndarray
        Pixel coordinates.
    """
    latmax = (size/2-.5) * spacing 
    lat = np.linspace(-latmax, latmax, size, endpoint=True)
    return lat
    
    

def get_fan_coords(size, spacing, distance, numang):
    """ Compute equispaced angular coordinates for 2d detector
    
    The centers of the pixels of a detector are usually not aligned to
    a pixel grid. If we center the detector at the origin, odd images
    will have a pixel at zero, whereas even images will have two pixels
    next to the actual center.
    We want to compute an equispaced array of `numang` angles that go
    between the centers of the outmost far pixels of the detector.
    
    Parameters
    ----------
    size : int
        Size of the detector (number of detection points).
    spacing : float
        Distance between two detection points in pixels.
    distance : float
        Axial distance from the detector to the angular measurement
        position in pixels.
    numang : int
        Number of angles.


    Returns
    -------
    angles, latpos : two 1D ndarrays
        Angles and pixel coordinates at the detector.
        
        
    Notes
    -----
    Actually one would not need to define spacing and distance, but for
    convenience, these parameters are separated and an arbitrary uint
    'pixel' is defined.
    """
    # Compute the angular positions of the outmost pixels
    latmax = (size/2-.5) * spacing
    angmax = abs(np.arctan2(latmax, distance))
    # equispaced angles
    angles = np.linspace(-angmax, angmax, numang, endpoint=True)
    
    latang = np.tan(angles)*distance
    latang[0] = -latmax
    latang[-1] = latmax
    
    return angles, latang



def radon(arr, angles, jmc=None, jmm=None):
    """ Compute the Radon transform (sinogram) of a circular image.


    The `scipy` Radon transform performs this operation on the 
    entire image, whereas this implementation requires an input
    image that has gray-scale values of 0 outside of a circle
    with diameter equal to the image size.


    Parameters
    ----------
    arr : ndarray, shape (N,N)
        the input image.
    angles : ndarray, length A
        angles or projections in radians
    jmc, jmm : instance of `multiprocessing.Value` or `None`
        The progress of this function can be monitored with the 
        `jobmanager` package. The current step `jmc.value` is
        incremented `jmm.value` times. `jmm.value` is set at the 
        beginning.
        

    Returns
    -------
    outarr : ndarray of floats, shape (A, N)
        Sinogram of the input image. The i'th row contains the
        projection data of the i'th angle.


    See Also
    --------
    scipy.ndimage.interpolation.rotate :
        The interpolator used to rotate the image.
    """
    # This function also works with single angles
    angles = np.atleast_1d(angles)
    A = angles.shape[0]
    N = len(arr)
    # The radon function from skimage.transform doeas not allow
    # to reshape the image (one could cut it of course).
    # Furthermore, no interpolation is used or at least I do not
    # know what kind of interpolation is used (_wharp_fast?).
    # outarray: x-axis: projection
    #           y-axis: 
    outarr = np.zeros((A, N))
    # jobmanager
    if jmm is not None:
        jmm.value = A + 1
    if jmc is not None:
        jmc.value += 1
        
    for i in np.arange(A):
        rotated = scipy.ndimage.rotate(arr, angles[i]/np.pi*180, order=3,
                  reshape=False, mode="constant", cval=0) #black corner
        # sum along some axis.
        outarr[i] = rotated.sum(axis=0)
        if jmc is not None:
            jmc.value += 1
    return outarr



def radon_fan_translation(arr, det_size, det_spacing=1, shift_size=1,
                          lS=1, lD=None, return_ang=False,
                          jmc=None, jmm=None):
    """ Compute the Radon transform for a fan beam geometry
        
    In contrast to `radon`, this function uses (1) a fan-beam geometry
    (the integral is taken along rays that meet at one point), and
    (2) translates the object laterally instead of rotating it. The
    result is sometimes referred to as 'linogram'.

    x
    ^ 
    |
    ----> z


    source       object   detector

              /             . (+det_size/2, lD)
    (0,-lS) ./   (0,0)      .
             \              .
              \             . (-det_size/2, lD)


    The algorithm computes all angular projections for discrete
    movements of the object. The position of the object is changed such
    that its lower boundary starts at (det_size/2, 0) and its upper
    boundary ends at (-det_size/2, 0) at increments of `shift_size`.


    Parameters
    ----------
    arr : ndarray, shape (N,N)
        the input image.
    det_size : int
        The total detector size in pixels. The detector centered to the
        source. The axial position of the detector is the center of the
        pixels on the far right of the object.
    det_spacing : float
        Distance between detection points in pixels.
    shift_size : int
        The amount of pixels that the object is shifted between
        projections.
    lS : multiples of 0.5
        Source position relative to the center of `arr`. lS >= 1.
    lD : int
        Detector position relative to the center `arr`. Default is N/2.
    return_ang : bool
        Also return the angles corresponding to the detector pixels.
    jmc, jmm : instance of `multiprocessing.Value` or `None`
        The progress of this function can be monitored with the 
        `jobmanager` package. The current step `jmc.value` is
        incremented `jmm.value` times. `jmm.value` is set at the 
        beginning.
        

    Returns
    -------
    outarr : ndarray of floats, shape (N+det_size,det_size)
        Linogram of the input image. Where N+det_size determines the
        lateral position of the sample.


    See Also
    --------
    scipy.ndimage.interpolation.rotate :
        The interpolator used to rotate the image.
    radontea.radon
        The real radon transform.
    """
    N = arr.shape[0]
    if lD is None:
        lD = N/2
    lS = abs(lS)
    lDS = lS + lD

    numsteps = int(np.ceil((N+det_size)/shift_size))
    
    if jmm is not None:
        jmm.value = numsteps + 2
    
    # First, create a zero-padded version of the input image such that
    # its center is the source - this is necessary because we can
    # only rotate through the center of the image.
    #arrc = np.pad(arr, ((0,0),(N+2*lS-1,0)), mode="constant")    
    if lS <= N/2:
        pad = 2*lS
        arrc = np.pad(arr, ((0,0),(pad,0)), mode="constant")
        # The center is where either b/w 2 pixels or at one pixel,
        # as it is for the input image.
    else:
        pad = N/2 + lS
        if pad%1 == 0: #even
            pad = int(pad)
            # We padd to even number of pixels.
            # The center of the image is between two pixels (horizontally).
            arrc = np.pad(arr, ((0,0),(pad,0)), mode="constant")
        else: #odd
            # We padd to odd number of pixels.
            # The center of the image is a pixel.
            pad = int(np.floor(pad))
            arrc = np.pad(arr, ((0,0),(pad,0)), mode="constant")
    
    # Lateral and axial coordinates of detector pixels
    axi = np.ones(det_size)*lDS
    # minus .5 because we use the center of the pixel
    
    if det_size%2 == 0: #even
        even = True
    else: #odd
        even = False

    if jmc is not None:
        jmc.value += 1

    lat = get_det_coords(det_size, det_spacing)

    angles = np.arctan2(lat,axi)
    
    # Before we can rotate the image for every lateral position of the
    # object, we need to zero-pad the image with the lateral detector
    # size. We pad only the bottom of the image, putting its center at 
    # the upper detector boundary.
    pad2 = det_size
    padset = np.pad(arrc, ((0,pad2), (0,0)), mode="constant")
    A = angles.shape[0]
    lino = np.zeros((numsteps, A))

    if jmc is not None:
        jmc.value += 1
    
    for i in range(numsteps):
        padset = np.roll(padset, shift_size, axis=0)
        # cut out a det_size slice
        curobj = padset[N:]
        for j in range(A):
            ang = angles[j]
            rotated = scipy.ndimage.rotate(curobj, ang/np.pi*180,
                        order=3, reshape=False, mode="constant", cval=0)
            if even:
                warnings.warn("For even images the linogram is of "+
                              "reduced resolution, because the center "+
                              "of the image does not coincide with "+
                              "a center of a pixel.")
                centerid = int(len(rotated)/2)
                lino[i,j] = np.sum(rotated[centerid-1:centerid+1, :])/2
            else: #odd
                centerid = int(np.floor(len(rotated)/2))
                lino[i,j] = np.sum(rotated[centerid, :])
        
        if jmc is not None:
            jmc.value += 1
            
    if return_ang:
        return lino, angles
    else:
        return lino


