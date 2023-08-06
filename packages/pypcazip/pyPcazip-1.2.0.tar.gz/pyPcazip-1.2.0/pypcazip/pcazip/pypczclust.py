#!/usr/bin/env python -W ignore
'''
                 *** The command line interface for pyPczclust ***                                                                                                                                  
'''

import logging as log

import numpy as np
from scipy import ndimage

import pcazip
from MDPlus.analysis.pca import pczfile

def watclust(projs, resolution=10):
    '''
    Watershed clustering. Given a set of coordinate data projs(N,D) where
    N is the number of points and D is the number of dimensions, returns
    a list of labels, of length N, identifying the cluster to which each
    point belongs. "resolution" specifies the number of bins for the
    underlying process of histogramming, and may be a single number or a
    list of length D.
    '''
    ndim = projs.shape[1]
    resol = np.zeros(ndim)
    resol[:] = resolution
    # set the boundaries, r, for the histogram. Include a buffer, so 
    # that there is a clear 1-bin boundary around the map.
    r = []
    min = projs.min(axis=0)
    max = projs.max(axis=0)
    for i in range(ndim):
        buff = (max[i]-min[i])/(resol[i]-2)*1.01
        r.append((min[i]-buff, max[i]+buff))
    # create the histogram
    H, edges = np.histogramdd(projs, bins=resol, range=r)

    # define the function that will locate local maxima in the distibution: 
    def f(arr):
        if np.argmax(arr) == len(arr)/2:
            return 1
        else:
            return 0
    # now find them (calling them 'labels' but at the moment they are
    # really 'maxima', will become labels properly next):
    labels = ndimage.filters.generic_filter(H,f,size=3,mode='constant')
    # now turn them into proper labels:
    ndimage.measurements.label(labels,output=labels)
    # now bump up H to name room in the low-order digits for the label
    maxval = np.max(labels)
    log.info("pyPczclust: {0} clusters found".format(int(maxval)))
    scale = int(10**np.ceil(np.log10(maxval)))
    H = H * scale + labels
    # Define the function that assigns bins to labels. For each currently
    # unlabelled bin, we search around to find the neighbour bin with
    # the highest occupancy. If this bin is already labelled, the current
    # bin gets this label too.
    def f2(arr,scale):
        cval = arr[len(arr)/2]
        if cval > 0 and cval%scale == 0:
            maxval = np.max(arr)
            if maxval%scale > 0:
                cval = cval +maxval%scale
        return cval

    # now we can do the watershed-like clustering. The process is iterative,
    # labels "spread out" in a downhill direction from the maxima until all
    # bins are labelled.
    Hnew = ndimage.filters.generic_filter(H,f2,size=3,mode='constant',extra_arguments=(scale,))
    while np.any(Hnew != H):
        H = Hnew
        Hnew = ndimage.filters.generic_filter(H,f2,size=3,mode='constant',extra_arguments=(scale,))

    H = H%scale
    # now we can go through the list of points and assign a cluster label
    # to each:
    tmplist = []
    for proj in projs:
        indx = []
        i = 0
        for c in proj:
            indx.append(np.digitize((c,c),edges[i])[0]-1)
            i += 1
        tmplist.append(H[tuple(indx)])
    # now reassign labels so largest group has label=1, etc.

    newlab = np.argsort(np.argsort(np.bincount(tmplist)))
    newlab = abs(newlab-newlab.max()) + 1

    out = []
    for i in tmplist:
        out.append(newlab[int(i)])

    # now mark "root" structures with negative indices:

    j =0
    for proj in projs:
        indx = []
        i = 0
        for c in proj:
            indx.append(np.digitize((c,c),edges[i])[0]-1)
            i += 1
        if labels[tuple(indx)] > 0:
            out[j] = -out[j]
        j += 1
    return out

def pczclust(args): 
    '''
    Performs histogram/watershed based clustering on data from a .pcz
    file.
    '''

    if args.verbosity:
        log.basicConfig(format="%(levelname)s: %(message)s", level=log.DEBUG)
        log.info("Verbose output")
    else:
        log.basicConfig(format="%(levelname)s: %(message)s")

    p = pczfile.Pczfile(args.pczfile)

    projs = np.zeros((p.nframes,args.dims))
    for i in range(args.dims):
        projs[:,i] = p.proj(i)

    out = watclust(projs, resolution=args.bins)
    np.savetxt(args.outfile,np.c_[projs,out], fmt=("%8.3f"*args.dims + "%5d"))
