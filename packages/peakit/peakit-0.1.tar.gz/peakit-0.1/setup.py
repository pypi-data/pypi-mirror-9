# -*- coding: utf8 -*-
__author__ = 'Clemens Prescher'

from distutils.core import setup
import os

setup(name="peakit",
      version='0.1',
      description="Interactive peak fitting software.",
      author='Clemens Prescher',
      author_email='clemens.prescher@gmail.com',
      url='https://github.com/Luindil/peakit',
      license='GPL3',
      platforms=['Windows', 'Linux', 'Mac OS X'],
      classifiers=['Intended Audience :: Science/Research',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python',
                   'Topic :: Scientific/Engineering',
      ],
      install_requires = ['numpy', 'scipy', 'pyqtgraph', 'lmfit', 'pyqtgraph'],
      packages=['peakit', 'peakit.controller', 'peakit.model', 'peakit.view', 'peakit.test'],
      package_data={'peakit.view':['*.qss', os.path.join('images', '*')],
                    'peakit.test':[os.path.join('data', '*')]},
      scripts=['scripts/peakit'])
