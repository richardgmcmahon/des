import sys

sys.path.append('/home/rgm/soft/python/lib/')
from librgm.plotid import plotid



def plot_radec_wisecat(data=None,
                       source=None, radius=3.0,
                       radec_centre=None,
                       fill=False,
                       colnames_radec=['RAJ2000', 'DEJ2000'],
                       xrange = [-2.5, 2.5],
                       yrange = [-2.5, 2.5],
                       overplot=True,
                       plt=None,
                       showplot=False,
                       debug=False):
    """

    # WISE W1 FWHM = 6.0 arcsecs
    radius = 6.0/2.0 = 3.0


    """

    import numpy as np
    from matplotlib.patches import Circle

    infile = None
    if 'filename' in data.meta:
        print('filename:', data.meta['filename'])
        infile = data.meta['filename']

    ra0 = radec_centre[0]
    dec0 = radec_centre[1]

    print('Number of rows:', len(data))
    if debug:
        data.info()
        data.info('stats')
        print('filename:', infile)
        print('ra0', ra0)
        print('dec0', dec0)
        print('xrange:', xrange)
        print('yrange:', yrange)

    index_column = -1
    try:
        index_column = data.index_column(colnames_radec[0])
    except:
        pass
    if index_column > -1:
        ra = data[colnames_radec[0]]

    index_column = -1
    try:
        index_column = data.index_column(colnames_radec[1])
    except:
        pass
    if index_column > -1:
        dec = data[colnames_radec[1]]


    ra_min = np.min(ra)
    ra_max = np.max(ra)
    delta_ra = (ra - ra0) * 3600.0 * np.cos(np.deg2rad(dec0))

    if debug:
        print('ndata', len(ra))
        print('ra_min:', ra_min)
        print('ra_max:', ra_max)
        print('Delta RA range:',
              np.min(delta_ra), np.max(delta_ra))

    dec_min = np.min(dec)
    dec_max = np.max(dec)
    delta_dec = (dec - dec0) * 3600.0

    if debug:
        print('dec_min:', dec_min)
        print('dec_max:', dec_max)
        print('Delta Dec range:',
              np.min(delta_dec), np.max(delta_dec))

    if debug:
        key=raw_input("Enter any key to continue: ")

    xdata = delta_ra
    ydata = delta_dec

    print(xrange)
    print(yrange)


    # include the psf radius so that sources that near edge are plotted
    itest = (xdata > (xrange[0] - radius)) & \
            (xdata < (xrange[1] + radius)) & \
            (ydata > (yrange[0] - radius)) & \
            (ydata < (yrange[1] + radius))

    xdata = xdata[itest]
    ydata = ydata[itest]
    ndata = len(xdata)

    if not overplot:
        plt.figure(figsize=(8,8))
        plt.axes().set_aspect('equal')

    patches = []
    ax = plt.gcf().gca()
    for x, y in zip(xdata, ydata):
        print(x, y, radius)
        circle = plt.Circle((x, y), radius, fill=fill,
                            color='red', alpha=0.1,
                            edgecolor='red',
                            linestyle='dashed', linewidth=1.0)
        ax.add_artist(circle)

        # draw line around edge with alpha = 1.0
        circle = plt.Circle((x, y), radius, fill=fill,
                            color='red', alpha=1.0,
                            edgecolor='red',
                            linestyle='dashed', linewidth=1.0)
        ax.add_artist(circle)

    ndata =  len(xdata)
    plt.plot(xdata, ydata, '+', color='red', label='WISE: ' + str(ndata))
    plt.xlim(xrange)
    plt.ylim(yrange)
    plt.legend(fontsize='small')

    plotfile = source + '_COADD_radec.png'
    plt.savefig(plotfile)
    #plt.clf()
    print('Saving: ', plotfile)


    if showplot:
        plt.show()

    return plt
