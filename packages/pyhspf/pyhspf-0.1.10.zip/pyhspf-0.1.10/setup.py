"""
This is the setup file.
"""

import os, sys, io, zipfile, shutil, pickle

from numpy.distutils.core import Extension, setup
from distutils            import sysconfig
from urllib               import request

_version   = '0.1.10'
_directory = '{}/pyhspf'.format(sysconfig.get_python_lib())

_d = (
"""PyHSPF contains a library of subroutines to run the Hydrological 
Simulation Program in Fortran (HSPF), Version 12.2, Python extensions to 
the HSPF library, and a series of classes for building HSPF input files, 
performing simulations, and postprocessing simulation results.  

HSPF requires flowline and catchment data for a stream network, land use 
data for the stream reach subbasins, time series data of climate 
parameters, and hydrology parameters for each land use category/subbasin.  
These data sources (with the exception of the hydrology parameters) can be 
supplied externally as needed (e.g., using Python extensions for 
geographic information systems (GIS) software). Alternatively, a 
series of preprocessing classes and routines were developed based on 
flowline and catchment data from the National Hydrolography Dataset 
Version 2 (NHDPlus), climate data from the National Climate Data Center, 
and landuse data from the National Agricultural Statitistics Service (NASS)
Cropland Data Layer (CDL). The "core" module requires NumPy, SciPy, and
Matplotlib, and can be used for generating input files. The preprocessing 
routines require GDAL, PyShp, and Pillow and make a series of specific
assumptions about the location and availability of data sources on the 
computer.

PyHSPF can be used to assimilate the data into an HSPF model, build the 
HSPF input files, simulate the model over a period of time, and then 
provide statistics and plots of the simulation output. A series 
of examples are provided to illustrate PyHSPF usage."""
)

_s = """Python Extensions for utilizing the Hydrological 
Simulation Program in Fortran (HSPF) Version 12.2"""

_l = """
PyHSPF, Version {}

Copyright (c) 2014, UChicago Argonne, LLC
All rights reserved.
Copyright 2014. UChicago Argonne, LLC. This software was produced under U.S. 
Government contract DE-AC02-06CH11357 for Argonne National Laboratory (ANL), 
which is operated by UChicago Argonne, LLC for the U.S. Department of Energy. 
The U.S. Government has rights to use, reproduce, and distribute this software.
NEITHER THE GOVERNMENT NOR UCHICAGO ARGONNE, LLC MAKES ANY WARRANTY, EXPRESS 
OR IMPLIED, OR ASSUMES ANY LIABILITY FOR THE USE OF THIS SOFTWARE.  If 
software is modified to produce derivative works, such modified software 
should be clearly marked, so as not to confuse it with the version available 
from ANL.

Additionally, redistribution and use in source and binary forms, with or 
without modification, are permitted provided that the following conditions 
are met:

1. Redistributions of source code must retain the above copyright notice, 
   this list of conditions and the following disclaimer. 
2. Redistributions in binary form must reproduce the above copyright notice, 
   this list of conditions and the following disclaimer in the documentation 
   and/or other materials provided with the distribution. 
3. Neither the name of UChicago Argonne, LLC, Argonne National Laboratory, 
   ANL, the U.S. Government, nor the names of its contributors may be used 
   to endorse or promote products derived from this software without specific 
   prior written permission. 

THIS SOFTWARE IS PROVIDED BY UCHICAGO ARGONNE, LLC AND CONTRIBUTORS "AS IS" 
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE 
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE 
ARE DISCLAIMED. IN NO EVENT SHALL UCHICAGO ARGONNE, LLC OR CONTRIBUTORS BE 
LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR 
CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF 
SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS 
INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN 
CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) 
ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE 
POSSIBILITY OF SUCH DAMAGE.
""".format(_version)

# minor issue with some windows

if os.name == 'nt':

    python = sys.executable[:-10]
    gnu = python + 'lib/site-packages/numpy/distutils/fcompiler/gnu.py'
    with open(gnu, 'r') as f: s = f.read()
    i = s.index('raise NotImplementedError')
    if s[i-5:i] != 'pass#': 
        s = s[:i] + 'pass#' + s[i:]
        with open(gnu, 'w') as f: f.write(s)

    # numpy/f2py need this configuration file setup to work right

    distfile = '{}/Lib/distutils/distutils.cfg'.format(python)
    if not os.path.isfile(distfile):
        print('adding a configuration file to the Python library...\n')
        with open(distfile, 'w') as f:
            f.write('[build]\ncompiler=mingw32')
    lflags = ['-static']

else: lflags = []

# any additional files that are needed (blank for now)

data_files = []

data_directory = sysconfig.get_python_lib()

# if the source files exists, install

package_data = ['hspfmsg.wdm', 'attributes']

# files

files = ['hspf13/{}'.format(f) 
         for f in os.listdir('hspf13') if f[-1] == 'c' or f[-1] == 'f']

fflags = ['-O3', '-fno-automatic', '-fno-align-commons']

setup(
    name = 'pyhspf',
    version = _version,
    description = _s,
    author = 'David Lampert',
    author_email = 'djlampert@gmail.com',
    url = 'http://www.anl.gov',
    license = _l,
    long_description = _d,
    keywords = ['hydrology', 
                'watershed modeling', 
                'GIS',
                ],
    platforms = ['Windows', 'Linux'],
    classifiers = [
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Development Status :: 4 - Beta',
        'Intended Audience :: Science/Research',
        ],
    packages = ['pyhspf', 
                'pyhspf.core', 
                'pyhspf.preprocessing', 
                'pyhspf.calibration',
                'pyhspf.forecasting',
                ],
    package_dir = {'pyhspf':        'pyhspf',
                   'core':          'pyhspf/core', 
                   'preprocessing': 'pyhspf/preprocessing', 
                   'calibration':   'pyhspf/calibration',
                   'forecasting':   'pyhspf/forecasting',
                   },
    package_data = {'pyhspf': ['HSPF13.zip'],
                    'pyhspf.core': package_data
                    },
    data_files = [(data_directory, data_files)],
    ext_modules=[Extension(name = 'hspf', 
                           sources = files, 
                           extra_link_args = lflags,
                           extra_f77_compile_args = fflags
                           )]
    )

