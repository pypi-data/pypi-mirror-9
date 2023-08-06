""" Utilities for converting an ascii table to hdf5 """
from __future__ import print_function
import os
from astropy.io import ascii

def replace_ext(filename, new_ext):
    '''replace a filename's extention with a new one'''
    if not new_ext.startswith('.'):
        new_ext = '.' + new_ext

    return '.'.join(filename.split('.')[:-1])  + new_ext


def ascii2hdf5(inputfile, outputfile, clobber=False, overwrite=True,
               verbose=False):
    """Convert a file to hdf5 using compression and path set to data"""
    if verbose:
        print('converting {} to {}'.format(inputfile, outputfile))
    
    tbl = ascii.read(inputfile)
    try:
        tbl.write(outputfile, format='hdf5', path='data', compression=True,
                  overwrite=overwrite)
    except:
        print('problem with {}'.format(inputfile))
        return

    if clobber:
        os.remove(inputfile)
        if verbose:
            print('removed {}'.format(inputfile))

    return
