#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Aleksandr Sizov <sizov@cs.uef.fi>
# Elie Khoury <Elie.Khoury@idiap.ch>
#
# Copyright (C) 2014-2015 
#   University of Eastern Finland, Joensuu, Finland 
#   Idiap Research Institute, Martigny, Switzerland
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

from setuptools import setup, find_packages

setup(
    name='xspear.fast_plda',
    version='1.1.1',
    description='Toolchains for speaker recognition and anti-spoofing using PLDA',

    url='http://pypi.python.org/pypi/spear.fast_plda',
    license='GPLv3',

    author='Aleksandr Sizov, Elie Khoury',
    author_email='sizov@cs.uef.fi, Elie.Khoury@idiap.ch',
    keywords='bob, xbob, xbob.db, speaker recognition, plda',

    # If you have a better, long description of your package, place it on the
    # 'doc' directory and then hook it here
    long_description=open('README.rst').read(),

    packages=find_packages(),

    namespace_packages = [
      'xspear',
    ],
    entry_points={
      'console_scripts': [
        'ivec_whitening_lnorm.py = xspear.fast_plda.script.ivec_whitening_lnorm:main',
        'ivec_whitening_lnorm_wccn.py = xspear.fast_plda.script.ivec_whitening_lnorm_wccn:main',
        'ivec_whitening_lnorm_lda.py = xspear.fast_plda.script.ivec_whitening_lnorm_lda:main',
        'svm.py = xspear.fast_plda.script.svm:main',
        'evaluate_new.py = xspear.fast_plda.script.evaluate_new:main',
        ],
      },
    

    install_requires=[
        "setuptools", # for whatever
        "gridtk",   # SGE job submission at Idiap
        "bob == 1.2.2",      # base signal proc./machine learning library
        # databases
        "xbob.db.verification.filelist",
        
    ],

    # Classifiers are important if you plan to distribute this package through
    # PyPI. You can find the complete list of classifiers that are valid and
    # useful here (http://pypi.python.org/pypi?%3Aaction=list_classifiers).
    classifiers = [
      'Development Status :: 4 - Beta',
      'Intended Audience :: Developers',
      'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
      'Natural Language :: English',
      'Programming Language :: Python',
      'Programming Language :: Python :: 3',
      'Topic :: Scientific/Engineering :: Artificial Intelligence',
    ],

)
