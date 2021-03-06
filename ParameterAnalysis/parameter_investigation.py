from __future__ import (print_function, division)

"""

Analysis of image catalogue parameters from:

DES
VHS
PS1
SDSS
DECALS

VIDEO/VEILS
HSC

LSST
EUCLID

Compare and contrast the try to homogenise

Other survey

DESDM file name data model
DES2327-5248_'WAVEBAND'_cat.fits where WAVEBAND = ['g', 'r', 'i', 'z', 'Y']

/data/desardata/Y1A1//DES2327-5248//DES2327-5248_i_cat.fits

163 columns
4 colours have 12 dimensions
Total number of dimemsions (163 - 4) + 48 = 207 dimensions

Could split them into categories:

Y1A1:

could add UCDs to DES etc to help!

(i)  centroid measurements

In pixel coordinates
2:  [X, Y]_IMAGE
8:  [X, Y][MODEL, PEAK, PSF, WIN]_IMAGE


In celestial sky coordinates
8: [ALPHA, DELTA][MODEL, PEAK, PSF, WIN]_J2000

** [ALPHA, DELTA]_J2000 are missing corresponding to [X, Y]_IMAGE

20 parameters


(ii) size and shape measurement

In pixel coordinates
4: [X, Y][MIN, MAX]_IMAGE
1: XY_IMAGE
1: XYWIN_IMAGE
2: [X, Y]2_IMAGE
2: [X, Y]2WIN_IMAGE


4: [A, B]MODEL_[IMAGE, WORLD]
4: ERR[A, B]MODEL_[IMAGE, WORLD]

2: [A,B]WIN_IMAGE  [no WORLD, check Y3 etc] ********
4: ERR[A,B]WIN_[IMAGE, WORLD]

ERRX2WIN_IMAGE

4: [A, B]_[IMAGE, WORLD]

2: THETA_[IMAGE, J2000]
2: THETAWIN_

2: DISK_ASPECT_[IMAGE, WORLD]
2: DISK_ASPECTERR_[IMAGE, WORLD]

2: DISK_SCALE_[IMAGE, WORLD]
2: DISK_SCALEERR_[IMAGE, WORLD]

2: DISK_THETA_[IMAGE, WORLD]
2: DISK_THETAERR_[IMAGE, WORLD]

ERRTHETA_IMAGE
ERRTHETA[MODEL, PSF, WIN]_[IMAGE, J2000] *** CHECK ID WORLD AND J2000 ARE SAME


ELLIP[1, 2]MODEL_[IMAGE, WORLD]

(iii)   flux measurements

BACKGROUND
THRESHOLD


(iv)  flux distribution measures

CHI2_DETMODEL
CHI2_MODEL
CHI2_PSF

(v) Other

CLASS_STAR

Y3A1

/data/desardata3/Y3A1/r2587/DES2327-5248/p01/cat/


"""


import os
import logging
import sys
import time
from time import strftime
from time import gmtime

import traceback
import inspect

import numpy as np
import matplotlib.pyplot as plt

import corner
from astropy.table import Table
import astropy.io.fits as fits
import astropy.io.fits.compression
from astropy.stats import mad_std

from moments2ellipse import *

sys.path.append('/home/rgm/soft/python/lib/')
sys.path.append('/home/rgm/soft/sreed/')

from librgm.table_stats import table_stats
from librgm.plotid import plotid


# /Users/rgm/soft/sreed/Possibles_Analysis.py
# import Possibles_Analysis as PA
# import stats
# from match_lists import match_lists as ml


def explore_table_header(table=None, infile=None, debug=True):
    """

    http://docs.astropy.org/en/stable/io/fits/

    read with astropy.Table and astropy.io.fits


    """

    from astropy.io import fits

    # read with astropy.io.fits
    hdulist = fits.open(infile)
    hdulist.info()

    # read astropy.Table
    table = Table.read(infile)

    # read the header using astropy.io.fits
    # returns a HDUList object
    # see also http://docs.astropy.org/en/stable/io/fits/api/headers.htm
    hdulist = fits.open(infile)
    # help(hdulist)
    print('type(hdulist):', type(hdulist))
    print('Number of HDUs:', len(hdulist))
    print('hdulist.filename:', hdulist.filename())

    if debug:
        raw_input("Enter any key to continue: ")
        print('hdulist.info():', hdulist.info())
        raw_input("Enter any key to continue: ")

    header = hdulist[1].header
    print('type(header):', type(header))

    if debug:
        raw_input("Enter any key to continue: ")

    help(header)

    fitscolumns = header.columns
    fitscolumns.info()

    if debug:
        raw_input("Enter any key to continue: ")


    print('loop over the header keywords, values:')
    for key in header.keys():
        print(header[key])


    sys.exit()

    return


def make_hist(xdata=None, column=None, units=None, comment=None,
              waveband=None,
              figpath=None,
              infile=None, filename=None, datapath=None,
              zoom=False, save=True):
    """

    make EDA univariate histogram plots

    """

    fig = plt.figure(figsize=(8.0, 8.0))

    # what does this do?
    ids = np.where((xdata == xdata))[0]
    xdata = xdata[ids]
    pers = np.percentile(xdata, [1.0, 99.0])
    keeps = np.where((xdata < pers[1]) & (xdata > pers[0]))[0]

    if zoom and len(keeps) > 1:
        xdata1 = xdata[keeps]
        nper = len(xdata1)
        ax1 = fig.add_subplot(121)
        ax2 = fig.add_subplot(122, sharey=ax1)
        ax2.get_yaxis().set_visible(False)
        ax2.hist(xdata1, bins=100, log=True,
                 range=(min(xdata1), max(xdata1)))
        ax2.set_title("1st - 99th %tile: " + str(nper))
        labels2 = ax2.get_xticks()
        ax2.set_xticklabels(labels2, rotation=270)
    else:
        ax1 = fig.add_subplot(111)

    nr = len(xdata)
    ax1.hist(xdata, bins=100, log=True,
             range=(min(xdata), max(xdata)))
    labels1 = ax1.get_xticks()[:-1]
    ax1.set_xticklabels(labels1, rotation=270)
    text = ("Min: " + str(min(xdata)) + "\nMax: " + str(max(xdata)) +
            "\nMedian: " + str(np.median(xdata)) + "\nSigma MAD: " +
            str(mad_std(xdata)) + "\n1st %ile: " +
            str(pers[0]) + "\n99th %ile: " + str(pers[1]))
    ax1.text(0.2, 0.7, text,
             transform=ax1.transAxes, bbox=dict(facecolor='blue', alpha=0.2))
    ax1.set_title("All points: " + str(nr))
    text = column + " / " + units + "\n" + comment
    ax1.text(0.5, 0.05, text,
             ha="center", transform=fig.transFigure)
    ax1.set_ylabel("Frequency")
    print(column, filename, waveband)
    fig.suptitle(column + ":" + filename + ':' + waveband, fontsize='small')
    plt.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.2, wspace=0.0)
    plotid()
    fig = plt.gcf()
    fig.set_size_inches(10.0, 8.0)

    plotid()
    if save:
        basename=os.path.basename(infile)
        figfile = figpath + '/' + basename + '_hist_' + column + ".png"
        print('Saving:', figfile)
        plt.savefig(figfile)
        plt.close()
    else:
        plt.show()


def histograms(datapath=None, filename=None, debug=False,
               columns=None, waveband=None, figpath=None,
               table=None, zoom=False, save=True):
    """

    DES2327-5248_'WAVEBAND'_cat.fits where WAVEBAND = ['g', 'r', 'i', 'z', 'Y']


    Example figfile: DES2327-5248_g_cat_COLUMN.png

    """

    print('datapath:', datapath)
    print('filename:', filename)
    print('waveband:', waveband)

    infile = datapath + '/' + filename
    basename = os.path.basename(infile)

    print('infile:', infile)
    print('basename:', basename)
    print('filename:', filename)

    t = Table.read(infile)

    # read the header using astropy.io.fits
    # returns a HDUList object
    # see also http://docs.astropy.org/en/stable/io/fits/api/headers.htm
    hdr = fits.open(infile)
    print('Number of HDUs:', len(hdr))
    print('filename:', hdr.filename)
    if debug:
        raw_input("Enter any key to continue: ")

    help(hdr)
    header = hdr[1].header
    help(header)
    fitscolumns = hdr[1].columns
    fitscolumns.info()


    for key in header.keys():
        print(header[key])

    for (icol, column) in enumerate(columns):
        column_list = list(t.columns)
        print(t[column].info)
        print(t[column].meta)
        print('icol, unit:', icol, t[column].unit)
        print(icol, column, t[column].dtype, waveband)
        print(type(t[column]), type(t[column][0]))

        if "-" not in column and not isinstance(t[column][0], basestring):
            xdata = np.array(t[column], dtype=np.float64)
            units = ''
            try:
                units = str(t[column].units)
            except:
                pass

            print(icol, column, units)

            i = column_list.index(column) + 1
            comment = "(" + hdr[1].header.comments["TTYPE" + str(i)] + ")"
            # loop through columns with >1 dimensions
            if len(xdata.shape) > 1:
                n = 0
                while n < len(t[column][0]):
                    xdata = t[column][:, n]
                    column1 = column + "_" + str(n + 1)
                    n += 1
                    print('column1:', column1)
                    print('column range:', np.min(xdata), np.max(xdata))
                    print('column range:', np.nanmin(xdata), np.nanmax(xdata))
                    xdata = xdata[~np.isnan(xdata)]
                    make_hist(xdata, column=column1, units=units,
                              comment=comment, waveband=waveband,
                              datapath=datapath,
                              filename=filename,
                              figpath=figpath,
                              infile=infile,
                              zoom=zoom, save=save)
            else:
                print('column range:', np.min(xdata), np.max(xdata))
                print('column range:', np.nanmin(xdata), np.nanmax(xdata))
                xdata = xdata[~np.isnan(xdata)]
                print('len(xdata):', len(xdata))
                if len(xdata) > 0:
                    make_hist(xdata=xdata, column=column, units=units,
                          comment=comment, waveband=waveband,
                          datapath=datapath,
                          filename=filename, figpath=figpath,
                          infile=infile,
                          zoom=zoom, save=save)

        elif "-" in column and not isinstance(t[column][0], basestring):
            l = column.index("-")
            col1 = column[:l]
            col2 = column[l + 1:]
            xdata = t[col1] - t[col2]
            units = str(t[col1].units)
            i1 = column_list.index(col1) + 1
            i2 = column_list.index(col2) + 1
            comment = "(" + hdr[1].header.comments["TTYPE" + str(i1)] + \
                " " + hdr[1].header.comments["TTYPE" + str(i2)] + ")"
            if len(xdata) > 1:
                #for xdata in t[col]:
                make_hist(xdata, column, units, comment, waveband,
                          file_start + file_end,
                          out_path, zoom=zoom, save=save)
            else:
                print("No data")

        else:
            print('Skiping string column')

    return

    #make_hist(xs, col, units, comment, band, file_start + file_end, out_path, zoom = zoom, save = save)

def plot_psfex_catpars():
    """

    from psfex/psfcat_analysis.py and psf_analysis.py

        # extract a flux/mag vector
        ydata = data['FLUX_APER'][:,7]


    """

    ydata = np.log10(ydata)

    print('len(xdata), len(ydata): ', len(xdata), len(ydata))
    print('min(xdata), max(xdata): ', min(xdata), max(xdata))
    print('min(ydata), max(ydata): ', min(ydata), max(ydata))


    #plt.plot(xdata, ydata, '.k')
    ndata=len(xdata)

    plt.scatter(xdata, ydata, marker='.', s=1, label=str(ndata))
    xrange=(-1.0,20.0)
    plt.xlim(xrange)
    plt.ylim(0.0,8.0)

    xline=xrange
    FLUX_SAT=65000
    yline=[np.log10(FLUX_SAT), np.log10(FLUX_SAT)]
    plt.plot(xline, yline, color='red')

    plt.ylabel('Log(FLUX_APER_8) (uncalibrated)')
    plt.xlabel('FLUX_RADIUS_HALF_LIGHT (pixels)')
    plt.legend()

    title= infile
    plt.title(title, fontsize='medium')
    plotid(progname=True)

    filename = os.path.basename(infile)

    plotfile= filename + '_flux_radius_v_flux_aper_8.png'

    plt.savefig(plotfile)
    plt.clf()
    print('Saving: ', plotfile)


    plt.figure(figsize=(8.0, 8.0))

    # extract a flux/mag vector
    xdata=data['FLUX_APER'][:,7]
    ydata=xdata/data['FLUXERR_APER'][:,7]

    #ydata=data['MAG_APER'][:,3]

    print('min(ydata), max(ydata): ', min(ydata), max(ydata))

    #add a nominal zeropoint
    #ydata=ydata[0:,2]+25.0
    xdata = np.log10(xdata)
    ydata = np.log10(ydata)

    print('len(xdata), len(ydata): ', len(xdata), len(ydata))
    print('min(xdata), max(xdata): ', min(xdata), max(xdata))
    print('min(ydata), max(ydata): ', min(ydata), max(ydata))

    #plt.plot(xdata, ydata, '.k')
    ndata=len(xdata)

    plt.scatter(xdata, ydata, marker='.', s=1, label=str(ndata))
    xrange=(0.0,8.0)
    plt.xlim(xrange)
    yrange=(-2.0,5.0)
    plt.ylim(yrange)


    FLUX_SAT=65000
    xline=[np.log10(FLUX_SAT), np.log10(FLUX_SAT)]
    yline=yrange
    plt.plot(xline, yline, color='red', linestyle='--')

    xline=xrange
    SAMPLE_MINSN=20
    yline=[np.log10(SAMPLE_MINSN), np.log10(SAMPLE_MINSN)]
    plt.plot(xline, yline, color='red', linestyle='--')

    SAMPLE_MAXELLIP=0.3


    plt.xlabel('Log(FLUX_APER_8) (uncalibrated)')
    plt.ylabel('S/N')
    plt.legend()

    title= infile
    plt.title(title, fontsize='medium')
    plotid(progname=True)

    filename = os.path.basename(infile)

    plotfile= filename + '_fluxerr_v_flux_aper_8.png'

    plt.savefig(plotfile)
    plt.clf()
    print('Saving: ', plotfile)

    return data


def image_shape(data=None,
                datapath=None, filename=None,
                waveband='i',
                figpath='./',
                debug=False):

    """
    explore the Sextractor image shape parameters

    http://sextractor.readthedocs.io/en/latest/Measurements.html

    Detection image:
    A_IMAGE
    B_IMAGE
    THETA_IMAGE

    Measurement image
    AWIN_IMAGE pix
    BWIN_IMAGE pix
    THETAWIN_IMAGE deg

    Also
    A_WORLD
    B_WORLD
    THETA_J2000
    ELONGATION
    FLUX_RADIUS

    ISOAREA_IMAGE   int32                pix2
    ISOAREAF_IMAGE   int32                pix2
    ISOAREA_WORLD float32                deg2
    ISOAREAF_WORLD float32                deg2

    FWHMPSF_IMAGE pix
    FWHMPSF_WORLD deg

    FWHM_IMAGE
    FWHM_WORLD

    """

    infile = datapath + filename

    print('infile:', infile)
    if data is None:
        hdulist = fits.open(infile)
        data = hdulist[1].data


    # compare ellipse shape parameters
    X2 = data['X2_IMAGE']
    Y2 = data['Y2_IMAGE']
    XY = data['Y2_IMAGE']
    ELONGATION = data['ELONGATION']

    A_moments, B_moments, THETA_moments = moments2ellipse(X2, Y2, XY)

    A = data["A_IMAGE"]
    B = data["B_IMAGE"]
    THETA = data['THETA_IMAGE']


    plt.figure(figsize=(6.0, 6.0))

    xdata = np.log10(A)
    ydata = np.log10(A_moments)
    ndata = len(xdata)
    plt.plot(xdata, ydata, "k.", ms=1, label=str(ndata))

    plt.xlabel('Log10(A_IMAGE)')
    plt.ylabel('Log10(A_IMAGE_moments)')
    plt.title(infile + ':' + waveband, fontsize='medium')
    plt.legend()
    plotid()

    plotfile = 'A_IMAGE_A_IMAGE_moments_' + waveband + '.png'
    print('Saving plotfile: ', plotfile)
    plt.savefig(plotfile)
    plt.show()

    # compare B
    xdata = np.log10(B)
    ydata = np.log10(B_moments)

    plt.figure(figsize=(6.0, 6.0))

    plt.plot(xdata, ydata, "k.", ms=1, label=str(ndata))

    plt.xlabel('Log10(B_IMAGE)')
    plt.ylabel('Log10(B_IMAGE_moments)')
    plt.title(infile + ':' + waveband, fontsize='medium')
    plt.legend()
    plotid()

    plotfile = 'B_IMAGE_B_IMAGE_moments_'  + waveband + '.png'
    print('Saving plotfile: ', plotfile)
    plt.savefig(plotfile)
    plt.show()


    # xdata = np.log10(THETA)
    # ydata = np.log10(THETA_moments)

    xdata = THETA
    ydata = THETA_moments

    print('xrange:', np.min(xdata), np.max(xdata))
    print('yrange:', np.min(ydata), np.max(ydata))

    plt.figure(figsize=(6.0, 6.0))
    plt.plot(xdata, ydata, "k.", ms=1, label=str(ndata))

    plt.xlabel('THETA_IMAGE')
    plt.ylabel('THETA_IMAGE_moments')
    plt.title(infile + ':' + waveband, fontsize='medium')
    plt.legend()
    plotid()

    plotfile = 'B_THETA_B_THETA_Moments_'  + waveband + '.png'
    print('Saving plotfile: ', plotfile)
    plt.savefig(plotfile)
    plt.show()


    # Ellipticity
    print()
    print('Ellipticity')
    plt.figure(figsize=(6.0, 6.0))

    xdata = (1 - (B/A))
    ydata = (1 - (B_moments/A_moments))

    print('xdata range:', np.min(xdata), np.max(xdata))
    print('xdata nanrange:', np.nanmin(xdata), np.nanmax(xdata))
    print('ydata range:', np.min(ydata), np.max(ydata))
    print('ydata nanrange:', np.nanmin(ydata), np.nanmax(ydata))

    xydata_max = np.max([np.nanmax(xdata), np.nanmax(ydata)])
    plt.plot(xdata, ydata, "k.", ms=1, label=str(ndata))
    plt.xlim(0.0, 1.0)
    plt.ylim(0.0, 1.0)
    plt.xlabel('Ellipticity: [A, B]_IMAGE')
    plt.ylabel('Ellipticity: [A, B]_IMAGE_Moments')
    plt.title(infile + ':' + waveband, fontsize='medium')
    plt.legend()

    plotid()

    plotfile = 'Ellipticity_Ellipticity_Moments'  + waveband + '.png'
    print('Saving plotfile: ', plotfile)
    plt.savefig(plotfile)
    plt.show()



    # Elongation
    xdata = np.log10(A/B)
    ydata = ELONGATION

    plt.figure(figsize=(6.0, 6.0))

    print('xdata range:', np.min(xdata), np.max(xdata))
    print('xdata nanrange:', np.nanmin(xdata), np.nanmax(xdata))
    print('ydata range:', np.min(ydata), np.max(ydata))
    print('ydata nanrange:', np.nanmin(ydata), np.nanmax(ydata))

    xydata_max = np.max([np.nanmax(xdata), np.nanmax(ydata)])
    plt.plot(xdata, ydata, "k.", ms=1, label=str(ndata))
    plt.xlim(0.0, xydata_max)
    plt.ylim(0.0, xydata_max)
    plt.xlabel('Elongation: A/B_IMAGE')
    plt.ylabel('Elongation')
    plt.title(infile + ':' + waveband, fontsize='medium')
    plt.legend()

    plotid()

    plotfile = 'ElongationAB_Elongation_'  + waveband + '.png'
    print('Saving plotfile: ', plotfile)
    plt.savefig(plotfile)
    plt.show()


    plt.figure(figsize=(6.0, 6.0))



    # FLUX_RADIUS
    # APER_MAG_8

    A = data["A_IMAGE"]
    B = data["B_IMAGE"]
    xdata = A * B
    xdata = np.log10(xdata)
    fwhm = data["FWHM_IMAGE"]
    ydata = np.log10(fwhm)
    plt.plot(xdata, ydata, "k.", ms=1)
    plt.xlabel("A_IMAGE * B_IMAGE")
    plt.ylabel("FWHM_IMAGE")
    plt.title(infile + ': ' + waveband, fontsize='small')
    plotid()

    plt.show()

    # compare Area estimators
    xdata = A * B
    xdata = np.log10(xdata)

    fwhm = data["FWHM_IMAGE"]
    #print sum(A0s - A1s)
    #print sum(B0s - B1s)
    #print fwhm1s**2/(A1s**2 + B1s**2)
    #plt.plot(fwhm1s**2, (A1s**2 + B1s**2), "k.")
    #plt.plot(fwhm1s**2, ((A1s+B1s)/2.0)**2, "r.")

    isoarea = data["ISOAREA_IMAGE"]
    ydata = np.log10(isoarea)
    ndata = len(xdata)

    plt.figure(figsize=(6.0, 6.0))

    plt.plot(xdata, ydata, "k.", ms=1, label=str(ndata))

    plt.xlabel("A_IMAGE * B_IMAGE")
    plt.ylabel("ISOAREA_IMAGE")
    plt.title(infile + ':' + waveband, fontsize='medium')
    plt.legend()

    plotid()
    plt.show()


    return


def kron_radius(dir, file_start, file_end, wavebands,
                tile=None,
                run=None):

    for waveband in wavebands:
        with fits.open(dir + file_start + waveband + file_end) as hlist:
            data = hlist[1].data
            ks = data["KRON_RADIUS"]
            print('min, max:', min(ks), max(ks))
            if waveband == "g":
                k0s = ks
            else:
                k1s = ks
                diffs = (k0s - k1s)
            ids = np.where((ks == 0))[0]
            ras = data["ALPHAWIN_J2000"][ids]
            decs = data["DELTAWIN_J2000"][ids]
            plt.plot(ras, decs, "k.")
            plt.show()

            n = 1000
            while n < 1010:
                RA = ras[n]
                DEC = decs[n]
                id = data["NUMBER"][n]
                PA.cutout_image("", RA, DEC, tile, run, id,
                                save=False, cat_info=True)
                plt.show()
                n += 1


def elongation(dir, file_start, file_end,
               wavebands, waveband='i',
               tile=None, run=None):
    """

    """
    with fits.open(dir + file_start + waveband + file_end) as hlist:
        data = hlist[1].data
        es = data["ELONGATION"]

    for (n, e) in enumerate(es):
        if e > 3.0:
            fig = PA.cutout_image("",
                                  data["ALPHAWIN_J2000"][n],
                                  data["DELTAWIN_J2000"][n],
                                  tile, run,
                                  data["NUMBER"][n], cat_info=True)
            plt.show()


def XY_min_max(dir, file_start, file_end,
               wavebands, waveband='i',
               tilename=None, run=None):
    band = "i"
    with fits.open(dir + file_start + waveband + file_end) as hlist:
        data = hlist[1].data
        xs = data["XMAX_IMAGE"] - data["XMIN_IMAGE"]

    for (n, x) in enumerate(xs):
        if x > 50.0:
            fig = PA.cutout_image("",
                                  data["ALPHAWIN_J2000"][n],
                                  data["DELTAWIN_J2000"][n],
                                  tilename, run,
                                  data["NUMBER"][n], cat_info=True)
            plt.show()


def isoarea(dir, file_start, file_end,
            wavebands, waveband='i',
            tilename=None, run=None):
    """

    """

    with fits.open(dir + file_start + waveband + file_end) as hlist:
        data = hlist[1].data
        xs = data["ISOAREA_IMAGE"]

    for (n, x) in enumerate(xs):
        if x == 0:
            fig = PA.cutout_image("",
                                  data["ALPHAWIN_J2000"][n],
                                  data["DELTAWIN_J2000"][n],
                                  tilename, run,
                                  data["NUMBER"][n], cat_info=True)
            #fig = PA.cutout_zoom("", data["ALPHAWIN_J2000"][n], data["DELTAWIN_J2000"][n], "DES0332-2749", data["NUMBER    "][n], save = False)
            plt.show()


def petro_radius(dir, file_start, file_end,
                 wavebands, waveband='i',
                 filename=None, run=None):

    with fits.open(dir + file_start + waveband + file_end) as hlist:
        data = hlist[1].data
        xs = data["PETRO_RADIUS"]

    for (n, x) in enumerate(xs):
        if x > 10:
            fig = PA.cutout_image("",
                                  data["ALPHAWIN_J2000"][n],
                                  data["DELTAWIN_J2000"][n],
                                  data["NUMBER"][n],
                                  cat_info=True)
            #fig = PA.cutout_zoom("", data["ALPHAWIN_J2000"][n], data["DELTAWIN_J2000"][n], "DES0332-2749", data["NUMBER    "][n], save = False)
            plt.show()


def FWHM(dir, file_start, file_end,
         wavebands, waveband='i',
         tilename=None, run=None):

    with fits.open(dir + file_start + waveband + file_end) as hlist:
        data = hlist[1].data
        xs = data["FWHM_IMAGE"]

    for (n, x) in enumerate(xs):
        if x == 0:
            fig = PA.cutout_image("",
                                  data["ALPHAWIN_J2000"][n],
                                  data["DELTAWIN_J2000"][n],
                                  tilename, run,
                                  data["NUMBER"][n],
                                  cat_info=True)
            #fig = PA.cutout_zoom("", data["ALPHAWIN_J2000"][n], data["DELTAWIN_J2000"][n], "DES0332-2749", data["NUMBER    "][n], save = False)
            plt.show()


def flux_radius(dir, file_start, file_end, wavebands):
    """

    """
    waveband = "i"
    with fits.open(dir + file_start + waveband + file_end) as hlist:
        data = hlist[1].data
        xs = data["FLUX_RADIUS"]

    for (n, x) in enumerate(xs):
        if x < 0:
            fig = PA.cutout_image("",
                                  data["ALPHAWIN_J2000"][n],
                                  data["DELTAWIN_J2000"][n],
                                  "DES0332-2749",
                                  "20130305000001_DES0332-2749",
                                  data["NUMBER"][n], cat_info=True)
            #fig = PA.cutout_zoom("", data["ALPHAWIN_J2000"][n], data["DELTAWIN_J2000"][n], "DES0332-2749", data["NUMBER    "][n], save = False)
            plt.show()


def fluxes(dir, file_start, file_end, wavebands):
    """

    """
    for waveband in wavebands:
        with fits.open(dir + file_start + waveband + file_end) as hlist:
            data = hlist[1].data
            fauto = data["FLUX_AUTO"]
            fmax = data["FLUX_MAX"]
            fmodel = data["FLUX_MODEL"]
            fpsf = data["FLUX_PSF"]
            mmax = data["MU_MAX"]
            thres = data["THRESHOLD"]
            mthres = data["MU_THRESHOLD"]

            #xs = np.log10(fmodel)
            xs = np.log10(fpsf)
            #xs = np.log10(fauto)
            #ys = np.log10(fmodel/fmax)
            ys = np.log10(fmodel / fmax)
            #ys = np.log10(fauto/fmax)
            #xlabel = "Log10(FLUX_MODEL)"
            xlabel = "Log10(FLUX_PSF)"
            #xlabel = "Log10(FLUX_AUTO)"
            #ylabel = "log10(FLUX_MODEL_div_FLUX_MAX)"
            ylabel = "log10(FLUX_PSF_div_FLUX_MAX)"
            #ylabel = "Log10(FLUX_AUTO_div_FLUX_MAX)"

            """
            fig = plt.figure()
            ax1 = fig.add_subplot(311)
            ax1.plot(xs, ys, "k.", ms = 1)
            ax1.axes.get_xaxis().set_visible(False)
            ax2 = fig.add_subplot(312, sharex = ax1)
            ax2.plot(xs, ys, "k.", ms = 1)
            labels2 = ax2.get_yticks()[:-1]
            ax2.set_yticklabels(labels2)
            pers = np.percentile(ys, [0.5, 99.5])
            ax2.set_ylim(pers[0], pers[1])
            ax2.axes.get_xaxis().set_visible(False)
            ax3 = fig.add_subplot(313, sharex = ax1)
            ax3.plot(xs, ys, "k.", ms = 1)
            pers = np.percentile(ys, [2.0, 98.0])
            ax3.set_ylim(pers[0], pers[1])
            ax3.set_xlabel(xlabel)
            labels3 = ax3.get_yticks()[:-1]
            ax3.set_yticklabels(labels3)
            plotid.plotid()
            plt.subplots_adjust(left=0.2, right=0.9, top=0.9, bottom=0.1, wspace = 0.0, hspace = 0.0)
            fig = plt.gcf()
            fig.set_size_inches(10.0,20.0)
            ax2.text(0.05, 0.5, ylabel, va = "center", transform = fig.transFigure, rotation = "vertical")
            plt.suptitle(file_start + band)
            #plt.savefig("/home/sr525/Graphs/Parameters/" + xlabel + "_v_" + ylabel + "_" + file_start + band + ".png")
            #plt.close()
            plt.show()
            """

            fig = plt.figure()
            ax = fig.add_subplot(111)
            ax.plot(xs, ys, "k.", ms=1)
            ax.set_xlabel(xlabel)
            ax.set_ylabel(ylabel)
            ax.set_title(file_start + ':' + waveband)
            plotid.plotid()
            medx = np.median(xs)
            medy = np.median(ys)
            MADx = stats.MAD(xs, medx)
            MADy = stats.MAD(ys, medy)
            maxx = max(xs)
            minx = min(xs)
            maxy = max(ys)
            miny = min(ys)
            text = ("Range x: %0.2f " % (min(xs)) +
                    "to %0.2f\n" % (max(xs)) +
                    "Range y: %0.2f " % (min(ys)) +
                    "- %0.2f\n" % (max(ys)) +
                    "Medians x: %0.2f" % (medx) +
                    " y: %0.2f\n" % (medy) +
                    "MADs x: %0.2f" % (MADx) +
                    " y: %0.2f\n" % (MADy) +
                    "Sigma MADs x: %0.2f" % (1.4826 * MADx) +
                    " y: %0.2f" % (1.4826 * MADy))

            ax.text(0.1, 0.7, text,
                    transform=ax.transAxes,
                    bbox=dict(facecolor='black', alpha=0.2))

            figpath = "/home/sr525/Graphs/Parameters/"
            plt.savefig(figpath +
                        xlabel + "_v_" + ylabel + "_" + file_start +
                        waveband + ".png")
            plt.close()
            #plt.show()

            """
            plt.plot(np.log10(fmax), fmax/mmax, "k.", ms = 1)
            plt.xlabel("log10(FLUX_MAX)")
            plt.ylabel("FLUX_MAX / MU_MAX")
            plt.title(file_start + band)
            plt.savefig("/home/sr525/Graphs/Parameters/Log10(FLUX_MAX)_v_FLUX_MAX_div_MU_MAX.png")
            plt.close()
            #plt.show()

            plt.plot((thres), thres/mthres, "k.", ms = 1)
            plt.xlabel("THRESHOLD")
            plt.ylabel("THRESHOLD / MU_THRESHOLD")
            plt.title(file_start + band)
            plt.savefig("/home/sr525/Graphs/Parameters/THRESHOLD_v_THRESHOLD_div_MU_THRESHOLD.png")
            plt.close()
            #plt.show()
            """


def ra_dec(dir, file_start, file_end, wavebands):
    """

    """
    rass = [[], [], [], [], []]
    decss = [[], [], [], [], []]
    numss = [[], [], [], [], []]
    for waveband in wavebands:
        b = wavebands.index(waveband)
        with fits.open(dir + file_start + waveband + file_end) as hlist:
            data = hlist[1].data
            ras = data["ALPHAWIN_J2000"]
            decs = data["DELTAWIN_J2000"]
            print(len(ras))
            rass[b] = ras
            decss[b] = decs
            numss[b] = data["NUMBER"]

    t = Table.read(dir + file_start[:-1] + ".fits")
    #dists, inds = ml(rass[0], decss[0], rass[1], decss[1], 0.0006)
    #dists1, inds1 = ml(rass[0], decss[0], rass[2], decss[2], 0.0006)
    #ids = np.where( (inds <> inds1) & (inds < len(rass[0])) )[0]
    #print ids
    #print len(ids)
    #inds = inds[ids]
    dists, inds = ml(t["ALPHAWIN_J2000_G"],
                     t["DELTAWIN_J2000_G"],
                     t["ALPHAWIN_J2000_R"],
                     t["DELTAWIN_J2000_R"],
                     0.0006)
    ids = np.where((inds == len(t)))[0]
    print(len(ids))
    t_odd = t[ids]
    n = 0
    #while n < len(t_odd):
    #    fig = PA.cutout_image("", t_odd["ALPHAWIN_J2000_G"][n], t_odd["DELTAWIN_J2000_G"][n], "DES0332-2749", "20130305000001_DES0332-2749", t_odd["COADD_OBJECTS_ID"][n], cat_info = True)
    #    plt.show()
    #    n += 1
    n = 0
    plt.plot(t["RA"], t["DEC"], "k.", ms=1)
    plt.show()

    #while n < len(t):
    #print t["RA"][n], np.mean([t["ALPHAWIN_J2000_G"][n], t["ALPHAWIN_J2000_R"][n], t["ALPHAWIN_J2000_I"][n], t["ALPHAWIN_J2000_Z"][n]])
    #if t["ALPHAWIN_J2000_Y"][n] > 53.5:
    #    PA.cutout_image("", t["ALPHAWIN_J2000_Z"][n], t["DELTAWIN_J2000_Z"][n], "DES0332-2749", "20130305000001_DES0332-2749", t["COADD_OBJECTS_ID"][n], cat_info = True)
    #    plt.show()
    #n += 1

    r = 0
    for ras in rass:
        print(ras[ids][0:10], decss[r][ids][0:10])
        plt.plot(ras, decss[r], "k.", ms=1)
        plt.show()
        r += 1


def background(dir, file_start, file_end, wavebands):
    for waveband in wavebands:
        with fits.open(dir + file_start + waveband + ".fits.fz") as hlist:
            im = hlist[1].data
            print(np.median(im))

        with fits.open(dir + file_start + waveband + file_end) as hlist1:
            data = hlist1[1].data
            print(np.median(data["BACKGROUND"]))


def chi(dir, file_start, file_end, wavebands):
    for waveband in wavebands:
        with fits.open(dir + file_start + waveband + file_end) as hlist:
            data = hlist[1].data
            xs = data["CHI2_PSF"]

        for (n, x) in enumerate(xs):
            if x > 7e+23:
                fig = PA.cutout_image("", data["ALPHAWIN_J2000"][n],
                                      data["DELTAWIN_J2000"][n],
                                      "DES0332-2749",
                                      "20130305000001_DES0332-2749",
                                      data["NUMBER"][n], cat_info=True)
                #fig = PA.cutout_zoom("", data["ALPHAWIN_J2000"][n],
                #data["DELTAWIN_J2000"][n], "DES0332-2749",
                #data["NUMBER"][n], save = False)

                plt.show()



def mk_filename_desdm(tilename=None, waveband=None,
                      des_release=None, product='coadd_cat'):

    if des_release == 'SVA1':
        filename_prefix = tilename + '_' + waveband

    if des_release == 'Y1A1':
        filename_prefix = tilename + '_' + waveband

    if des_release == 'Y3A1':
        filename_prefix = tilename + '_' + run + '_' + waveband

    filename_tail = '_cat.fits'
    filename = filename_prefix + filename_tail

    return filename


def des_analysis(datapath=None,
                 tilename=None,
                 wavebands=None,
                 columns=None,
                 des_release=None,
                 figpath=None,
                 debug=False):
    """
    columns are passed as input to allow specification of columns
    to analyse

    """

    print('wavebands:', wavebands)
    for waveband in wavebands:

        filename = mk_filename_desdm(tilename=tilename,
                                     waveband=waveband,
                                     des_release=des_release)

        infile = datapath + '/' + filename

        print('tilename:', tilename)
        print('filename:', filename)
        print('infile:', infile)
        print('waveband:', waveband)

        raw_input("Enter any key to continue: ")

        image_shape(datapath=datapath, filename=filename,
                    waveband=waveband, figpath=figpath,
                    debug=DEBUG)

        raw_input("Enter any key to continue: ")

    for waveband in wavebands:

        filename = mk_filename_desdm(tilename=tilename,
                                     waveband=waveband,
                                     des_release=des_release)

        infile = datapath + '/' + filename

        print('filename:', filename)
        print('infile:', infile)
        print('waveband:', waveband)

        if DEBUG:
            raw_input("Enter any key to continue: ")

        histograms(datapath=datapath, filename=filename,
                   columns=columns, waveband=waveband, figpath=figpath,
                   zoom=True, debug=DEBUG)


    filename_prefix = mk_filename_desdm(tilename=tilename,
                                        waveband=waveband,
                                        des_release=des_release)

    # filename_tail = '_cat.fits'



    kron_radius(dir, file_start, file_end, wavebands,
                tile=tile, run=run)

    elongation(dir, file_start, file_end, wavebands,
               tile=tile, run=run)


def ps1_analysis(datapath=None, filename=None,
                 columns=None, waveband='',
                 debug=False):


        infile = datapath + '/' + filename

        print('filename:', filename)
        print('infile:', infile)
        print('waveband:', waveband)

        if DEBUG:
            raw_input("Enter any key to continue: ")

        histograms(datapath=datapath, filename=filename,
                   columns=columns, figpath=figpath,
                   waveband=waveband, debug=DEBUG,
                   zoom=True)


def generic_analysis(datapath=None, filename=None,
                    columns=None,
                    figpath=None,
                    explore_header=False,
                    debug=False):


        print('datapath:', datapath)
        print('filename:', filename)

        infile = datapath + '/' + filename

        print('filename:', filename)
        print('infile:', infile)
        print('waveband:', waveband)

        if explore_header:
            raw_input("Enter any key to continue: ")
            explore_table_header(table=None, infile=infile,
                debug=DEBUG)

        if DEBUG:
            raw_input("Enter any key to continue: ")

        histograms(datapath=datapath, filename=filename,
                   columns=columns, figpath=figpath,
                   waveband='',
                   zoom=True, debug=DEBUG)

def corner_example(scatter=False):
    # Set up the parameters of the problem.
    ndim, nsamples = 3, 50000

    # Generate some fake data.
    np.random.seed(42)


    # // Floor Division
    print(ndim * 4 * nsamples // 5)
    print(4 * nsamples // 5, ndim)

    data1 = np.random.randn(ndim * 4 * nsamples // 5).reshape([4 * nsamples // 5, ndim])
    print('data1.shape:', data1.shape)

    data2 = (4*np.random.rand(ndim)[None, :] + np.random.randn(ndim * nsamples // 5).reshape([nsamples // 5, ndim]))
    print('data2.shape:', data2.shape)


    data = np.vstack([data1, data2])
    # data = data1
    # data = data2

    print('data.shape:', data.shape)

    # Plot it.
    figure = corner.corner(data, verbose=True,
                           labels=[r"$x$", r"$y$", r"$\log \alpha$", r"$\Gamma \, [\mathrm{parsec}]$"],
                            quantiles=[0.159, 0.500, 0.841],
                            show_titles=True, title_kwargs={"fontsize": 12})

    plt.show()

    plt.savefig('corner_example.png')

    return


def corner_example_table(table, scatter=False,
                         colnames=['X_IMAGE', 'Y_IMAGE',
                                   'XWIN_IMAGE', 'YWIN_IMAGE',
                                   'XPEAK_IMAGE', 'YPEAK_IMAGE']):

    print(colnames)
    # Set up the parameters of the problem.
    ndim, nsamples = 3, 50000

    # help(table)
    print('len(table):', len(table))
    print('len(table.columns):', len(table.columns))
    print(table.columns)

    # Generate some fake data.
    # // Floor Division
    print(ndim * 4 * nsamples // 5)
    print(4 * nsamples // 5, ndim)
    np.random.seed(42)
    data1 = np.random.randn(ndim * 4 * nsamples // 5)
    print('data1.shape:', data1.shape, len(data1))
    data1 = data1.reshape([4 * nsamples // 5, ndim])
    print('data1.shape:', data1.shape, len(data1))

    data2 = (4*np.random.rand(ndim)[None, :] + np.random.randn(ndim * nsamples // 5).reshape([nsamples // 5, ndim]))
    print('data2.shape:', data2.shape, len(data2))

    data = np.hstack((table[colnames[0]], table[colnames[1]],
                      table[colnames[2]], table[colnames[3]],
                      table[colnames[4]], table[colnames[5]]))

    print('table version: data.shape:', data.shape, len(data))
    data = data.reshape(len(data) // 6, 6)
    print('table version(reshaped): data.shape:', data.shape, len(data))

    data = np.array([table[colnames[0]], table[colnames[1]],
                     table[colnames[2]], table[colnames[3]],
                     table[colnames[4]], table[colnames[5]]])
    data = np.transpose(data)

    print('table version: data.shape:', data.shape, len(data))


    # data = data1
    # data = data2

    plt.plot(table[colnames[0]], table[colnames[1]], '.',
             ms=1, markeredgecolor='none')
    plt.axis('equal')
    # ax.set_aspect('equal')
    plt.xlabel(colnames[0])
    plt.ylabel(colnames[1])
    plt.show()

    print('data.shape:', data.shape)

    # Plot it.
    figure = corner.corner(data, verbose=True, scatter=scatter,
                           labels=colnames,
                           quantiles=[0.159, 0.500, 0.841],
                           show_titles=True, title_kwargs={"fontsize": 'small'})

    plt.show()

    plt.savefig('corner_example_1.png')

    data = np.array([table['X_IMAGE'] - table['XWIN_IMAGE'],
                     table['X_IMAGE'] - table['XPEAK_IMAGE'],
                     table['X_IMAGE'] - table['XPSF_IMAGE']])
    colnames = ['(X-XWIN)_IMAGE', '(X-XPEAK)_IMAGE',
                '(X-XPSF)_IMAGE']
    print('data.shape:', data.shape)

    data = np.transpose(data)
    print('data.shape:', data.shape)

    figure = corner.corner(data, verbose=True, scatter=scatter,
                           labels=colnames,
                           quantiles=[0.159, 0.500, 0.841],
                           show_titles=True,
                           title_kwargs={"fontsize": 'small'})

    plt.show()

    plt.savefig('corner_example_2.png')




    return


def getargs():

    # setup argparse
    description = 'Catalogue parameter analysis'
    epilog = """Uses both command line arguments and a config file;
                command line arguements over ride config parameters;
                it is possible that not all config file parameters have
                command line options and all combinations have been tested.
             """
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description=description, epilog=epilog)

    config_file_default = 'ParameterAnalyis.cfg'
    parser.add_argument ("--config_file",
                         default=config_file_default,
                         type=str,
                         help="configuration file")

    survey_project_default = 'DES'
    parser.add_argument ("--survey_project",
                         default=survey_project_default,
                         help="Survey project e.g. DES, PS1, SDSS, VHS")

    data_product_default = 'COADD'

    data_release_default = 'Y1A1'
    parser.add_argument ("--data_release",
                         default=data_release_default,
                         help="DES data release")

    parser.add_argument ("--waveband",
                         default=None,
                         help="process a single waveband")

    parser.add_argument ("--datapath",
                         default=None,
                         help="""
                              optional path for input data; overrides
                              config file""")

    parser.add_argument ("--filename",
                         default=None,
                         help="filename for input data; overrides config file")

    parser.add_argument ("--figpath",
                         default='./',
                         help="path for output figures")

    parser.add_argument("--corner", action="store_true",
                        help="corner plot")

    parser.add_argument("--verbose", action="store_true",
                        help="optional verbose mode")

    parser.add_argument("--debug", action="store_true",
                        help="optional debug i.e. very verbose mode")


    print('Number of arguments:', len(sys.argv), 'arguments: ', sys.argv[0])
    args = parser.parse_args()

    return args


if __name__ == '__main__':
    """


    """
    # import doctest
    # doctest.testmod()

    # place after __main__ unless needed by functions prior to __main__
    # The ConfigParser module has been renamed to configparser
    import ConfigParser as configparser
    import argparse

    t0 = time.time()

    args = getargs()

    # logging.basicConfig(
    #    level=logging.INFO,
    #    format='%(asctime)s %(name)s %(levelname)-8s %(message)s')

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s.%(msecs)02d %(levelname)s %(name)s' \
               '%(module)s - %(funcName)s: %(message)s',
               datefmt="%Y-%m-%d %H:%M:%S")

    logger = logging.getLogger(__name__)

    DEBUG = args.debug

    config = configparser.ConfigParser()
    config_file = args.config_file

    logger.info('Reading configuration from %s' %(config_file))
    config.read(config_file)
    print(config.sections())
    for section in config.sections():
        print("Section: %s" % section)
        for options in config.options(section):
            print("%s = %s %s" % (options,
                                   config.get(section, options),
                                   str(type(options))))

    if DEBUG:
        raw_input("Enter any key to continue: ")

    # reduce the logging level
    logger.setLevel(logging.WARNING)
    if args.verbose:
        logging.info('Will produce verbose output')
        logging.setLevel(logging.DEBUG)

    survey_project = args.survey_project

    filename = args.filename

    if args.datapath is None:
        datapath_root = config.get(survey_project, 'datapath_root')
    if args.datapath is not None:
        datapath_root = args.datapath
    print('datapath_root:', datapath_root)

    if survey_project == 'DES':
        des_release = config.get('DEFAULT', 'des_release')
        print('des_release:', des_release)

        tilename = config.get('DEFAULT', 'tilename')
        print('tilename:', tilename)

        # Note 'run' is deprecated/redefined in DES Y3A1
        run = config.get('DEFAULT', 'run')
        print('run:', run)

    if args.datapath is not None:
        datapath = args.datapath

    if args.datapath is None:
        figpath = config.get(survey_project, 'figpath')
    if args.datapath is not None:
        figpath = args.figpath

    print('figpath:', figpath, os.path.exists(figpath))
    if not os.path.exists(figpath):
        print('Creating:', figpath)
        os.mkdir(figpath)

    # build the data path and input filename
    if survey_project == 'DES':
        datapath = datapath_root + '/' + des_release + '/' + tilename + '/'
    if survey_project == 'PS1':
        filename = config.get(survey_project, 'filename')
        datapath = datapath_root + '/'

    print('datapath:', datapath)

    wavebands = ["g", "r", "i", "z", "Y"]
    # wavebands = ['i']
    # wavebands = ["g", "r", "z", "Y"]
    if args.waveband is not None:
        wavebands = args.waveband

    waveband = wavebands[0]
    logging.info('survey_project:' + str(survey_project))
    logging.info('args.filename:' + str(args.filename))
    if survey_project == 'DES' and args.filename is None:
        filename = mk_filename_desdm(tilename=tilename, waveband=waveband,
                                     des_release=des_release)
        logging.info('filename:' + str(filename))

    logging.info('datapath:' + str(datapath))
    if args.datapath is None and args.filename is not None:
        datapath = ''
    if args.datapath is not None:
        datapath = args.datapath
    logging.info('datapath:' + str(datapath))

    if args.filename is not None:
        filename = args.filename
        # over ride default datapath some filename
        if args.datapath is None:
            datapath = ''

    logging.info('datapath:' + str(datapath))
    logging.info('filename:' + str(filename))

    infile = datapath + '/' + filename

    logging.info('infile:' + str(infile))

    print('wavebands:', wavebands)
    if DEBUG:
        raw_input("Enter any key to continue: ")

    print('Reading:', infile)
    print('Elapsed time(secs): ',time.time() - t0)
    t = Table.read(infile)
    print('Elapsed time(secs): ',time.time() - t0)
    t.meta['filename'] = infile

    t.info()
    t.info('stats')
    # table_stats(t)

    columns = t.columns
    print('Number of columns:', len(columns))
    print('Number of row:', len(t))
    if DEBUG:
        raw_input("Enter any key to continue: ")


    if args.corner is True:
        if DEBUG:
            help(corner)
        corner_example_table(t, scatter=False)

        corner_example_table(t, scatter=True)

        corner_example_table(t, scatter=False,
                             colnames=['A_IMAGE', 'B_IMAGE',
                                       'THETA_IMAGE', 'ELONGATION'])
        corner_example_table(t, scatter=True,
                             colnames=['A_IMAGE', 'B_IMAGE',
                                       'THETA_IMAGE', 'ELONGATION'])

        if DEBUG:
            print('corner plot completed')
            raw_input("Enter any key to continue: ")


    if args.filename is not None:
        filename = args.filename
        print('filename:', filename)
        if args.figpath is not None:
            figpath = args.figpath

        print('figpath:', figpath, os.path.exists(figpath))
        if not os.path.exists(figpath):
            print('Creating:', figpath)
            os.mkdir(figpath)

        explore_header = True
        generic_analysis(datapath=datapath, filename=filename,
                         columns=columns,
                         explore_header=explore_header,
                         figpath=figpath, debug=DEBUG)

    if survey_project == 'DES':
        des_analysis(datapath=datapath,
                     tilename=tilename,
                     wavebands=wavebands,
                     columns=columns,
                     des_release=des_release,
                     figpath=figpath,
                     debug=DEBUG)


    if survey_project == 'PS1':
        ps1_analysis(datapath=datapath, filename=filename,
                     columns=columns,
                     debug=DEBUG)

    # original tile
    # tile = "DES0332-2749"
    # run = "20130305000001_DES0332-2749"

    # Fernanda's lense tile
    # tilename = 'DES2327-n5248'
    # run = 'Y3A1'

    #dir = "/data/desardata/SVA1/DES1000+0209/"
    #t = Table.read(dir + "DES1000+0209_i_cat.fits")
    #dir = "/data/desardata/SVA1/DES0332-2749/"
    #cols = t.columns
    #cols = ["A_IMAGE", "B_IMAGE", "XMAX_IMAGE-XMIN_IMAGE", "
    # YMAX_IMAGE-YMIN_IMAGE", "A_WORLD", "B_WORLD", "ISOAREA_WORLD",
    # "ISOAREA_IMAGE", "ISOAREAF_IMAGE", "KRON_RADIUS", "PETRO_RADIUS",
    # "FWHM_IMAGE", "FWHM_WORLD", "THETA_IMAGE", "ELONGATION",
    # "FLUX_RADIUS", "AMODEL_IMAGE", "BMODEL_IMAGE", "THETAMODEL_IMAGE",
    # "AMODEL_WORLD", "BMODEL_WORLD", "THETAMODEL_J2000", "THETA_J2000",
    #"ISOAREAF_WORLD"]
    #cols = ["BMODEL_WORLD"]

    #file_start = "DES0332-2749_"

    file_start = "DES0332-2749_"
    file_end = "_cat.fits"
    # file_start = "DES1000+0209_"
    dir = "/data/desardata/SVA1/" + file_start[:-1] + "/"
    path = "/data/desardata/SVA1/" + file_start[:-1] + "/"

    for file_start in ["DES0332-2749_", "DES1000+0209_", "DES0453-4457_"]:
        infile = path + "/" + file_start + "i" + file_end
        print('infile:', infile)
        t = Table.read(infile)
        cols = t.columns
        histograms(path + "/", file_start, file_end, cols, wavebands,
                   zoom=True)

    image_shape(dir, file_start, file_end, wavebands)

    kron_radius(dir, file_start, file_end, wavebands,
                tile=tile, run=run)
    elongation(dir, file_start, file_end, wavebands,
               tile=tile, run=run)

    #XY_min_max(dir, file_start, file_end, wavebands)
    #isoarea(dir, file_start, file_end, wavebands)
    #petro_radius(dir, file_start, file_end, wavebands)
    #FWHM(dir, file_start, file_end, wavebands)
    #fluxes(dir, file_start, file_end, wavebands)
    #flux_radius(dir, file_start, file_end, wavebands)
    #ra_dec(dir, file_start, file_end, wavebands)
    #background(dir, file_start, file_end, wavebands)
    #chi(dir, file_start, file_end, wavebands)
