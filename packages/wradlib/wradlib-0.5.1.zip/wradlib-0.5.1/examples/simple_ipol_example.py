#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      Maik Heistermann
#
# Created:     12/09/2014
# Copyright:   (c) heistermann 2014
# Licence:     MIT
#-------------------------------------------------------------------------------
#!/usr/bin/env python

def ex_simple_ipol():

    import wradlib
    import numpy as np
    import pylab as pl

    # Your grid margin coordinates
    x = np.arange(0,10,1)
    y = np.arange(10,20,1)
    # Combine them to a full grid
    src = wradlib.util.gridaspoints(y,x)
    print "Shape of source coordinate array:", src.shape

    # Generate some random grid data
    # See that you grid is basically a one dimensional vector
    vals = np.arange(len(src)).astype("f4")
    print "Shape of grid values:", vals.shape
    # You need to reshape it in order to make it a "real" grid
    grid = np.reshape(vals, ( len(x),len(y) ) )

    # Let' assume that you have clutter at the following indices
    clutter = np.array([22,44,55,66])
    # Contaminate your original grid with clutter
    vals[clutter] = np.nan
    # These are the clutter coordinates
    trg = src[clutter,:]
    print "Shape of target coordinate array:", (trg.shape)

    # Now use the ipol module to fill the clutter
    out = wradlib.ipol.interpolate(src, trg, vals, Interpolator=wradlib.ipol.Idw)
    print "Shape of interpolation output:", out.shape

    # Now your filled grid will be
    filled_vals = vals.copy()
    filled_vals[clutter] = out
    # and if you want to go back to actual grid representation
    filled_grid = np.reshape(filled_vals, ( len(x),len(y) ) )

    # Compare (uncomment if you want to see the plots)
    ##fig = pl.figure()
    ##ax = pl.subplot(121)
    ##pm = pl.pcolormesh(np.ma.masked_invalid(grid))
    ##pl.colorbar(pm)
    ##ax = pl.subplot(122)
    ##pm = pl.pcolormesh(np.ma.masked_invalid(filled_grid))
    ##pl.colorbar(pm)
    ##pl.show()

if __name__ == '__main__':
    ex_ipol()







