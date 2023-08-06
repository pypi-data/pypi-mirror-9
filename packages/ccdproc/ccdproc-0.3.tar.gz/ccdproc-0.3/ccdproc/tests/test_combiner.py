# Licensed under a 3-clause BSD style license - see LICENSE.rst
# This module implements the base CCDData class.
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import numpy as np

import astropy.units as u
from astropy.stats import median_absolute_deviation as mad

from astropy.tests.helper import pytest


from ..ccddata import CCDData
from ..combiner import *


#test that the Combiner raises error if empty
def test_combiner_empty():
    with pytest.raises(TypeError):
        Combiner()  # empty initializer should fail


#test that the Combiner raises error if empty if ccd_list is None
def test_combiner_init_with_none():
    with pytest.raises(TypeError):
        Combiner(None)  # empty initializer should fail


#test that Combiner throws an error if input
#objects are not ccddata objects
def test_ccddata_combiner_objects(ccd_data):
    ccd_list = [ccd_data, ccd_data, None]
    with pytest.raises(TypeError):
        Combiner(ccd_list)  # different objects should fail


#test that Combiner throws an error if input
#objects do not have the same size
def test_ccddata_combiner_size(ccd_data):
    ccd_large = CCDData(np.zeros((200, 100)), unit=u.adu)
    ccd_list = [ccd_data, ccd_data, ccd_large]
    with pytest.raises(TypeError):
        Combiner(ccd_list)  # arrays of different sizes should fail


#test that Combiner throws an error if input
#objects do not have the same units
def test_ccddata_combiner_units(ccd_data):
    ccd_large = CCDData(np.zeros((100, 100)), unit=u.second)
    ccd_list = [ccd_data, ccd_data, ccd_large]
    with pytest.raises(TypeError):
        Combiner(ccd_list)


#test if mask and data array are created
def test_combiner_create(ccd_data):
    ccd_list = [ccd_data, ccd_data, ccd_data]
    c = Combiner(ccd_list)
    assert c.data_arr.shape == (3, 100, 100)
    assert c.data_arr.mask.shape == (3, 100, 100)


#test if dtype matches the value that is passed
def test_combiner_dtype(ccd_data):
    ccd_list = [ccd_data, ccd_data, ccd_data]
    c = Combiner(ccd_list, dtype = np.float32)
    assert c.data_arr.dtype == np.float32
    avg = c.average_combine()
    # dtype of average should match input dtype
    assert avg.dtype == c.dtype
    med = c.median_combine()
    # dtype of median should match dtype of input
    assert med.dtype == c.dtype


#test mask is created from ccd.data
def test_combiner_mask(ccd_data):
    data = np.zeros((10, 10))
    data[5, 5] = 1
    mask = (data == 0)
    ccd = CCDData(data, unit=u.adu, mask=mask)
    ccd_list = [ccd, ccd, ccd]
    c = Combiner(ccd_list)
    assert c.data_arr.shape == (3, 10, 10)
    assert c.data_arr.mask.shape == (3, 10, 10)
    assert not c.data_arr.mask[0, 5, 5]


def test_weights(ccd_data):
    ccd_list = [ccd_data, ccd_data, ccd_data]
    c = Combiner(ccd_list)
    with pytest.raises(TypeError):
        c.weights = 1


def test_weights_shape(ccd_data):
    ccd_list = [ccd_data, ccd_data, ccd_data]
    c = Combiner(ccd_list)
    with pytest.raises(ValueError):
        c.weights = ccd_data.data


#test the min-max rejection
def test_combiner_minmax(ccd_data):
    ccd_list = [CCDData(np.zeros((10, 10)), unit=u.adu),
                CCDData(np.zeros((10, 10)) - 1000, unit=u.adu),
                CCDData(np.zeros((10, 10)) + 1000, unit=u.adu)]

    c = Combiner(ccd_list)
    c.minmax_clipping(min_clip=-500, max_clip=500)
    ccd = c.median_combine()
    assert ccd.data.mean() == 0


def test_combiner_minmax_max(ccd_data):
    ccd_list = [CCDData(np.zeros((10, 10)), unit=u.adu),
                CCDData(np.zeros((10, 10)) - 1000, unit=u.adu),
                CCDData(np.zeros((10, 10)) + 1000, unit=u.adu)]

    c = Combiner(ccd_list)
    c.minmax_clipping(min_clip=None, max_clip=500)
    assert c.data_arr[2].mask.all()


def test_combiner_minmax_min(ccd_data):
    ccd_list = [CCDData(np.zeros((10, 10)), unit=u.adu),
                CCDData(np.zeros((10, 10)) - 1000, unit=u.adu),
                CCDData(np.zeros((10, 10)) + 1000, unit=u.adu)]

    c = Combiner(ccd_list)
    c.minmax_clipping(min_clip=-500, max_clip=None)
    assert c.data_arr[1].mask.all()


def test_combiner_sigmaclip_high():
    ccd_list = [CCDData(np.zeros((10, 10)), unit=u.adu),
                CCDData(np.zeros((10, 10)) - 10, unit=u.adu),
                CCDData(np.zeros((10, 10)) + 10, unit=u.adu),
                CCDData(np.zeros((10, 10)) - 10, unit=u.adu),
                CCDData(np.zeros((10, 10)) + 10, unit=u.adu),
                CCDData(np.zeros((10, 10)) + 1000, unit=u.adu)]

    c = Combiner(ccd_list)
    #using mad for more rubust statistics vs. std
    c.sigma_clipping(high_thresh=3, low_thresh=None, func=np.median,
                     dev_func=mad)
    assert c.data_arr[5].mask.all()


def test_combiner_sigmaclip_single_pix():
    ccd_list = [CCDData(np.zeros((10, 10)), unit=u.adu),
                CCDData(np.zeros((10, 10)) - 10, unit=u.adu),
                CCDData(np.zeros((10, 10)) + 10, unit=u.adu),
                CCDData(np.zeros((10, 10)) - 10, unit=u.adu),
                CCDData(np.zeros((10, 10)) + 10, unit=u.adu),
                CCDData(np.zeros((10, 10)) - 10, unit=u.adu)]
    c = Combiner(ccd_list)
    #add a single pixel in another array to check that
    #that one gets rejected
    c.data_arr[0, 5, 5] = 0
    c.data_arr[1, 5, 5] = -5
    c.data_arr[2, 5, 5] = 5
    c.data_arr[3, 5, 5] = -5
    c.data_arr[4, 5, 5] = 25
    c.sigma_clipping(high_thresh=3, low_thresh=None, func=np.median,
                     dev_func=mad)
    assert c.data_arr.mask[4, 5, 5]


def test_combiner_sigmaclip_low():
    ccd_list = [CCDData(np.zeros((10, 10)), unit=u.adu),
                CCDData(np.zeros((10, 10)) - 10, unit=u.adu),
                CCDData(np.zeros((10, 10)) + 10, unit=u.adu),
                CCDData(np.zeros((10, 10)) - 10, unit=u.adu),
                CCDData(np.zeros((10, 10)) + 10, unit=u.adu),
                CCDData(np.zeros((10, 10)) - 1000, unit=u.adu)]

    c = Combiner(ccd_list)
    #using mad for more rubust statistics vs. std
    c.sigma_clipping(high_thresh=None, low_thresh=3, func=np.median,
                     dev_func=mad)
    assert c.data_arr[5].mask.all()


#test that the average combination works and returns a ccddata object
def test_combiner_median(ccd_data):
    ccd_list = [ccd_data, ccd_data, ccd_data]
    c = Combiner(ccd_list)
    ccd = c.average_combine()
    assert isinstance(ccd, CCDData)
    assert ccd.shape == (100, 100)
    assert ccd.unit == u.adu
    assert ccd.meta['NCOMBINE'] == len(ccd_list)


#test that the median combination works and returns a ccddata object
def test_combiner_average(ccd_data):
    ccd_list = [ccd_data, ccd_data, ccd_data]
    c = Combiner(ccd_list)
    ccd = c.average_combine()
    assert isinstance(ccd, CCDData)
    assert ccd.shape == (100, 100)
    assert ccd.unit == u.adu
    assert ccd.meta['NCOMBINE'] == len(ccd_list)


#test data combined with mask is created correctly
def test_combiner_mask_average(ccd_data):
    data = np.zeros((10, 10))
    data[5, 5] = 1
    mask = (data == 0)
    ccd = CCDData(data, unit=u.adu, mask=mask)
    ccd_list = [ccd, ccd, ccd]
    c = Combiner(ccd_list)
    ccd = c.average_combine()
    assert ccd.data[0, 0] == 0
    assert ccd.data[5, 5] == 1
    assert ccd.mask[0, 0]
    assert not ccd.mask[5, 5]


def test_combiner_with_scaling(ccd_data):
    # The factors below are not particularly important; just avoid anything
    # whose average is 1.
    ccd_data_lower = ccd_data.multiply(3)
    ccd_data_higher = ccd_data.multiply(0.9)
    combiner = Combiner([ccd_data, ccd_data_higher, ccd_data_lower])
    # scale each array to the mean of the first image
    scale_by_mean = lambda x: ccd_data.data.mean()/np.ma.average(x)
    combiner.scaling = scale_by_mean
    avg_ccd = combiner.average_combine()
    # Does the mean of the scaled arrays match the value to which it was
    # scaled?
    np.testing.assert_almost_equal(avg_ccd.data.mean(),
                                   ccd_data.data.mean())
    assert avg_ccd.shape == ccd_data.shape
    median_ccd = combiner.median_combine()
    # Does median also scale to the correct value?
    np.testing.assert_almost_equal(np.median(median_ccd),
                                   np.median(ccd_data.data))

    # Set the scaling manually...
    combiner.scaling = [scale_by_mean(combiner.data_arr[i]) for i in range(3)]
    avg_ccd = combiner.average_combine()
    np.testing.assert_almost_equal(avg_ccd.data.mean(),
                                   ccd_data.data.mean())
    assert avg_ccd.shape == ccd_data.shape


def test_combiner_scaling_fails(ccd_data):
    combiner = Combiner([ccd_data, ccd_data.copy()])
    # Should fail unless scaling is set to a function or list-like
    with pytest.raises(TypeError):
        combiner.scaling = 5


#test data combined with mask is created correctly
def test_combiner_mask_media(ccd_data):
    data = np.zeros((10, 10))
    data[5, 5] = 1
    mask = (data == 0)
    ccd = CCDData(data, unit=u.adu, mask=mask)
    ccd_list = [ccd, ccd, ccd]
    c = Combiner(ccd_list)
    ccd = c.median_combine()
    assert ccd.data[0, 0] == 0
    assert ccd.data[5, 5] == 1
    assert ccd.mask[0, 0]
    assert not ccd.mask[5, 5]
