#!/usr/bin/env python

from distutils.core import setup, Extension
from Cython.Distutils import build_ext
import numpy
import os, glob
import sys

# include numpy directories for extensions
numpyincludedirs = numpy.get_include()

# read version number from version file
path = os.path.abspath( os.curdir )
Ctrax_path = os.path.join( path, 'Ctrax' )
ver_filename = os.path.join( Ctrax_path, 'version.py' )
ver_file = open( ver_filename, "r" )
for line in ver_file: # parse through file version.py
    if line.find( '__version__' ) >= 0:
        line_sp = line.split() # split by whitespace
        version_str = line_sp[2] # third item
        this_version = version_str[1:-1] # strip quotes
ver_file.close()

# write version number to text file
ver_filename = os.path.join( path, 'version.txt' )
ver_file = open( ver_filename, "w" )
ver_file.write( '%s\n'%this_version )
ver_file.close()

# add all of the .xrc and .bmp files
# where 6 == len( 'Ctrax/' )
Ctrax_package_data = [ f[6:] for f in glob.glob(os.path.join('Ctrax','xrc','*.xrc'))]+\
                     [ f[6:] for f in glob.glob(os.path.join('Ctrax','icons','*.ico'))]+\
                     [ f[6:] for f in glob.glob(os.path.join('Ctrax','xrc','*.bmp'))]


# determine setup config for psutil (1.0.1)
# POSIX
if os.name == 'posix':
    posix_extension = Extension('_psutil_posix',
                                sources = ['psutil/_psutil_posix.c'])
# Windows
if sys.platform.startswith("win32"):

    def get_winver():
        maj, min = sys.getwindowsversion()[0:2]
        return '0x0%s' % ((maj * 100) + min)

    psutil_extensions = [Extension('_psutil_mswindows',
                                   sources=['psutil/_psutil_mswindows.c',
                                            'psutil/_psutil_common.c',
                                            'psutil/arch/mswindows/process_info.c',
                                            'psutil/arch/mswindows/process_handles.c',
                                            'psutil/arch/mswindows/security.c'],
                                   define_macros=[('_WIN32_WINNT', get_winver()),
                                                  ('_AVAIL_WINVER_', get_winver())],
                                   libraries=["psapi", "kernel32", "advapi32",
                                              "shell32", "netapi32", "iphlpapi",
                                              "wtsapi32"],
                                   #extra_compile_args=["/Z7"],
                                   #extra_link_args=["/DEBUG"]
                                   )]
# OS X
elif sys.platform.startswith("darwin"):
    psutil_extensions = [Extension('_psutil_osx',
                                   sources = ['psutil/_psutil_osx.c',
                                              'psutil/_psutil_common.c',
                                              'psutil/arch/osx/process_info.c'],
                                   extra_link_args=['-framework', 'CoreFoundation',
                                                    '-framework', 'IOKit']
                                   ),
                         posix_extension]
# Linux
elif sys.platform.startswith("linux"):
    psutil_extensions = [Extension('_psutil_linux',
                                   sources=['psutil/_psutil_linux.c'],
                                   ),
                         posix_extension]



long_description = """
Ctrax: The Caltech Multiple Fly Tracker

(c) 2007-2014 The Caltech Ethomics Project
http://ctrax.sourceforge.net
bransonk@janelia.hhmi.org

Ctrax is an open-source, freely available, machine vision program for
estimating the positions and orientations of many walking flies,
maintaining their individual identities over long periods of time. It
was designed to allow high-throughput, quantitative analysis of
behavior in freely moving flies. Our primary goal in this project is
to provide quantitative behavior analysis tools to the neuroethology
community, thus we've endeavored to make the system adaptable to other
labs' setups. We have assessed the quality of the tracking results for
our setup, and found that it can maintain fly identities indefinitely
with minimal supervision, and on average for 1.5 fly-hours
automatically.
"""

classifiers=[
    'Development Status :: 4 - Beta',
    'Intended Audience :: Developers',
    'Intended Audience :: End Users/Desktop',
    'Intended Audience :: Information Technology',
    'Intended Audience :: Science/Research',
    'License :: OSI Approved :: GNU General Public License (GPL)',
    'Natural Language :: English',
    'Operating System :: Microsoft :: Windows',
    'Operating System :: MacOS :: MacOS X',
    'Operating System :: POSIX :: Linux',
    'Programming Language :: C',
    'Programming Language :: C++',
    'Programming Language :: Python :: 2.7',
    'Topic :: Scientific/Engineering',
    'Topic :: Scientific/Engineering :: Artificial Intelligence',
    'Topic :: Scientific/Engineering :: Bio-Informatics',
    'Topic :: Scientific/Engineering :: Image Recognition',
    'Topic :: Scientific/Engineering :: Information Analysis',
    'Topic :: Scientific/Engineering :: Medical Science Apps.',
    ]

requires=['cython',
          'matplotlib',
          'motmot.imops',
          'motmot.ufmf',
          'motmot.wxvalidatedtext',
          'motmot.wxvideo',
          'numpy',
          'opencv',
          'PIL',
          'scipy',
          'wx',
          ]

extensions = [Extension('hungarian',['hungarian/hungarian.cpp',
                                     'hungarian/asp.cpp'],
                        include_dirs=[numpyincludedirs,]),
              Extension('houghcircles_C',
                        ['houghcircles/houghcircles_C.c'],
                        include_dirs=[numpyincludedirs,]),
              Extension('kcluster2d',
                        ['kcluster2d/kcluster2d_cython.pyx'],
                        include_dirs=[numpyincludedirs,]),
              Extension('tracking_funcs',
                        ['tracking_funcs/tracking_funcs.pyx'],
                        include_dirs=[numpyincludedirs,])
              ]
# If this line errors, you're not building on a known platform.
extensions.extend( psutil_extensions )

setup( name="Ctrax",
       version=this_version,
       author="Caltech Ethomics Project",
       author_email="bransonk@janelia.hhmi.org",
       maintainer="Kristin Branson",
       maintainer_email="bransonk@janelia.hhmi.org",
       url="http://ctrax.sourceforge.net",
       description="Ctrax: The Caltech Multiple Fly Tracker",
       long_description=long_description,
       download_url="http://sourceforge.net/projects/ctrax/",
       classifiers=classifiers,
       platforms=['Windows','Linux','MacOS X'],
       requires=requires,
       provides=['Ctrax'],
       obsoletes=['mtrax'],
       scripts=['Ctrax/Ctrax'],
       cmdclass = {'build_ext': build_ext},
       packages=['Ctrax', 'psutil'],
       package_dir={'Ctrax': 'Ctrax', 'psutil': 'psutil'},
       package_data = {'Ctrax':Ctrax_package_data},
       ext_modules=extensions
      )
