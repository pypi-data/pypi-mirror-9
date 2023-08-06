"""
DynaMIT
-------------

A Python library implementing a dynamic and extensible biological motifs integration toolkit.

DynaMIT is distributed under the GPLv3 License.
"""

from setuptools import setup
from dynamit import __version__

# performs package installation
setup(
	name='DynaMIT',
	packages=['dynamit'],
	version=__version__,
	description='the Dynamic Motif Integration Toolkit',
	long_description=__doc__,
	author='Erik Dassi',
	author_email='erik.dassi@unitn.it',
	url='https://bitbucket.org/erikdassi/dynamit',
	classifiers=[
		'Programming Language :: Python',
		'Programming Language :: Python :: 2',
		'Programming Language :: Python :: 3',
		'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
		'Operating System :: OS Independent',
		'Development Status :: 5 - Production/Stable',
		'Environment :: Console',
		'Intended Audience :: Science/Research',
		'Topic :: Scientific/Engineering :: Bio-Informatics'
	],
	install_requires=['biopython>=1.65', 'scikit-learn>=0.15.2', "scipy>=0.14.0",
										'numpy>=1.9.1', 'matplotlib>=1.4.2', 'weblogo>=3.4'],
	package_data={'dynamit': ['graphics/*.*']}
)
