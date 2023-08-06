# Prefer setuptools over distutils
# Ref: http://gpiot.com/blog/creating-a-python-package-and-publish-it-to-pypi/
from setuptools import setup, find_packages
#from distutils.core import setup

setup(
	name = 'rocksolid-agent',
	#include_package_data=True,
	version = '1.0.14',
	description = 'rocksolid security agent. Find and mitigate outdated software/apps on your server',
	author = 'rocksolid',
	author_email = 'hello@rocksolid.io',
	url = 'https://github.com/rocksolid-io/rocksolid-agent', # use the URL to the github repo
	download_url = 'https://github.com/rocksolid-io/rocksolid-agent/tarball/1.0.13', # I'll explain this in a second
	keywords = ['rocksolid', 'agent', 'scan', 'security', 'cms', 'packages', 'vulnerability'], # arbitrary keywords
	classifiers = [],
	packages = find_packages(),

	package_dir = {'rocksolid_agent': 'rocksolid_agent'},
        # If there are data files included in your packages that need to be
        # installed in site-packages, specify them here.  If using Python 2.6 or less, then these
        # have to be included in MANIFEST.in as well.
        package_data={
                'rocksolid_agent':
                        ['rocksolid-agent.cat',
                        'rocksolid-agent.def',
                        'LICENSE.txt',
                        'libs/*'],
        },

        # To provide executable scripts, use entry points in preference to the
        # "scripts" keyword. Entry points provide cross-platform support and allow
        # pip to create the appropriate form of executable for the target platform.
        entry_points={
                'console_scripts': [
                        ['rocksolid-agent = rocksolid_agent.rocksolid_agent:main'],
                ],
        },
)
