#!/usr/bin/env python3
#
# File: extract_NCDC.py
#
# by David J. Lampert, PhD, PE (djlampert@gmail.com)
#
# Last updated: 06/13/2014
#
# Purpose: imports climate data files to Python classes

import os, pickle, io, shutil

from urllib    import request
from shapefile import Reader

from .climateutils import find_ghcnd
from .climateutils import find_gsod
from .climateutils import find_precip3240
from .climateutils import find_nsrdb

def is_integer(s):
    """Tests if string "s" is an integer."""
    try: int(s) 
    except ValueError: return False
    return True

def get_boundaries(shapes, space = 0.1):
    """Gets the boundaries for the plot."""

    boundaries = shapes[0].bbox
    for shape in shapes[0:]:
        b = shape.bbox
        if b[0] < boundaries[0]: boundaries[0] = b[0]
        if b[1] < boundaries[1]: boundaries[1] = b[1]
        if b[2] > boundaries[2]: boundaries[2] = b[2]
        if b[3] > boundaries[3]: boundaries[3] = b[3]

    xmin = boundaries[0] - (boundaries[2] - boundaries[0]) * space
    ymin = boundaries[1] - (boundaries[3] - boundaries[1]) * space
    xmax = boundaries[2] + (boundaries[2] - boundaries[0]) * space
    ymax = boundaries[3] + (boundaries[3] - boundaries[1]) * space

    return xmin, ymin, xmax, ymax

def decompress7z(filename, directory,
                 path_to_7z = r'C:/Program Files/7-Zip/7z.exe'):
    """Decompresses a Unix-compressed archive on Windows using 7zip."""

    c = '{0} e {1} -y -o{2}'.format(path_to_7z, filename, directory)

    subprocess.call(c)

def decompresszcat(filename, directory):
    """Decompresses a Unix-compressed archive on Windows using 7zip."""

    with subprocess.Popen(['zcat', filename], 
                          stdout = subprocess.PIPE).stdout as s:

        with open(filename[:-2], 'wb') as f: f.write(s.read())
 
def extract_ghcnd(directory, HUC8, start, end, types = 'all', space = 0.1,
                  GHCND = 'http://www1.ncdc.noaa.gov/pub/data/ghcn/daily',
                  verbose = True):
    """Extracts data from GHCND Stations."""

    # make a folder for the files

    d = '{}/{}/GHCND'.format(directory, HUC8)
    if not os.path.isdir(d): 
        os.mkdir(d)
        if verbose: print('downloading data from GHCND\n')

    # find the bounding box

    boundaryfile = '{0}/{1}/{1}boundaries'.format(directory, HUC8)

    boundaryreader = Reader(boundaryfile)
    bbox = get_boundaries(boundaryreader.shapes(), space = space)
    
    # find stations in the bounding box

    stations = find_ghcnd(bbox, types = types, dates = (start, end))

    # iterate through the stations and download the data

    for station in stations: station.download_data(d, start = start, end = end)

    # check to see that the data needed are there

    stations = []
    for f in os.listdir(d):
        if f[-3:] != 'png':
            with open('{}/{}'.format(d, f), 'rb') as g:
                station = pickle.load(g)
            stations.append(station)

    if space < 0.5: space = 0.5
    while all([len([d for d, e in s.evap if 0 <= e and start <= d and 
                    d <= end]) == 0 for s in stations]):
        print('no evaporation records available, looking for evaporation data')
        bbox = get_boundaries(boundaryreader.shapes(), space = space)
        print('bounding box: {:.2f}, {:.2f}, {:.2f}, {:.2f}'.format(*bbox))
        extrastations = find_ghcnd(bbox, var = 'EVAP', 
                                   dates = (start, end), verbose = verbose)

        for s in extrastations: 
            s.download_data(d, start = start, end = end)
            if len(s.evap) > 0:
                stations.append(s)

        space += 0.5

def extract_gsod(directory, HUC8, start, end, space = 0.1,
                 verbose = False):

    # make a folder for the files

    d = '{}/{}/GSOD'.format(directory, HUC8)
    if not os.path.isdir(d): os.mkdir(d)

    # open up the bounding box for the watershed

    boundaryfile = '{0}/{1}/{1}boundaries'.format(directory, HUC8)

    boundaryreader = Reader(boundaryfile)
    bbox = get_boundaries(boundaryreader.shapes(), space = space)

    # find the stations in the bounding box

    stations = find_gsod(bbox)

    years = [s.start.year for s in stations if s.start is not None]

    # if more data are needed, expand the bounding box

    if space <= 0.5: space = 0.5
    while all([start.year < y for y in years]): 
        print('GSOD files in the watershed do not contain sufficient data')
        print('looking for other stations')

        bbox = get_boundaries(boundaryreader.shapes(), space = space)
        stations += find_gsod(bbox, dates = (start, end))
        years = [s.start.year for s in stations if s.start is not None]
        space += 0.2
    
    # iterate through the stations and download the data

    for station in stations: station.download_data(d, start = start, end = end)

    # combine together stations in different files (why did they do this???)

    combined = []
    for station in stations:
        var = d, station.airforce, station.wban
        source = '{0}/{1:06d}-{2:05d}'.format(*var)
        
        if station.airforce == 999999:
            var = d, station.wban
            destination = '{0}/{1:05d}'.format(*var)
        else:
            var = d, station.airforce
            destination = '{0}/{1:06d}'.format(*var)

        if os.path.isfile(destination):
            with open(destination, 'rb') as f: existing = pickle.load(f)
            with open(source, 'rb') as f:      adding   = pickle.load(f)
            existing.add_data(adding)
            with open(destination, 'wb') as f: pickle.dump(existing, f)
        elif os.path.isfile(source): 
            shutil.copy(source, destination)
            combined.append(destination)

    # print the output

    for p in combined:
        with open(p, 'rb') as f: station = pickle.load(f)
        station.plot(start, end, output = p)

def extract_precip3240(directory, HUC8, start, end, 
                       NCDC = 'ftp://ftp.ncdc.noaa.gov/pub/data',
                       clean = False, space = 0.2, verbose = True):
    """Makes a point shapefile of the stations from a csv file of hourly 
    precipitation data from NCDC within the bounding box of the watershed."""

    if os.name == 'nt': decompress = decompress7z
    else:               decompress = decompresszcat

    d = '{}/{}/precip3240'.format(directory, HUC8)
    if not os.path.isdir(d): os.mkdir(d)

    # open up the bounding box for the watershed

    boundaryfile = '{0}/{1}/{1}boundaries'.format(directory, HUC8)

    boundaryreader = Reader(boundaryfile)

    bbox = get_boundaries(boundaryreader.shapes(), space = space)

    # find the precipitation stations in the bounding box

    stations = find_precip3240(bbox, verbose = verbose)

    if verbose: print('')

    # make a list of all the states since that's how the NCDC data are stored

    states = list(set([s.code for s in stations]))

    # download the state data for each year
    
    for state in states: download_state_precip3240(state, d, verbose = verbose)

    archives = ['{}/{}'.format(d, a) for a in os.listdir(d)
                if a[-6:] == '.tar.Z']

    for a in archives:

        # decompress the archive

        if not os.path.isfile(a[:-2]): 
            decompress(a, d)
            if verbose: print('')
            
    # import the data

    for station in stations: station.import_data(d, start, end)

def extract_nsrdb(directory, HUC8, start, end, space = 0.1,
                  plot = True, verbose = True, vverbose = False):
    """Makes pickled instances of the GageStation class for all the gages
    meeting the calibration criteria for an 8-digit watershed."""

    if verbose: print('\nextracting solar radiation data from NREL\n')

    # paths for the watershed shapefiles

    boundaryfile = '{0}/{1}/{1}boundaries'.format(directory, HUC8)
    solarfile    = '{0}/{1}/{1}solarstations'.format(directory, HUC8)

    # make a folder for the files

    d = '{0}/{1}/NSRDB'.format(directory, HUC8)
    if not os.path.isdir(d): os.mkdir(d)

    boundaryreader = Reader(boundaryfile)

    stations = []
    while len(stations) == 0:
        
        bbox = get_boundaries(boundaryreader.shapes(), space = space)
        stations = find_nsrdb(bbox, dates = (start, end))
        space += 0.2

    # download the data

    print('')
    for station in stations: 
        
        if not os.path.isfile('{}/{}'.format(d, station.usaf)):

            station.download_data(d, dates = (start, end))

    # plot it up

    from pyhspf.preprocessing.climateplots import plot_nsrdb

    for station in stations: 

        p = '{}/{}'.format(d, station.usaf)
        if not os.path.isfile(p + '.png'):

            with open(p, 'rb') as f: s = pickle.load(f) 

            try: plot_nsrdb(s, start, end, output = p)
            except: print('unable to plot', s.station)   

def download_climate(directory, HUC8, start, end):
    """Downloads select climate data from GHCND, GSOD, NSRDB, and NCDC 3240."""
    
    # download the GHCND data

    if not os.path.isdir('{}/{}/GHCND'.format(directory, HUC8)):
        extract_ghcnd(directory, HUC8, start, end)

    # download the GSOD data

    if not os.path.isdir('{}/{}/GSOD'.format(directory, HUC8)):
        extract_gsod(directory, HUC8, start, end)

    # download the hourly precipitation data from NCDC

    if not os.path.isdir('{}/{}/precip3240'.format(directory, HUC8)):
        extract_precip3240(directory, HUC8, start, end)

    # download the NSRDB data

    if not os.path.isdir('{}/{}/NSRDB'.format(directory, HUC8)):
        extract_nsrdb(directory, HUC8, start, end)

