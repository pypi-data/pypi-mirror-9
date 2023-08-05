import os

here=os.path.dirname(os.path.abspath(__file__))

from distutils import sysconfig
from setuptools import setup

site_packages_path = sysconfig.get_python_lib()

# Get the long description from the relevant file
with open(os.path.join(here, 'DESCRIPTION.rst')) as f:
    long_description = f.read()

setup(
    name='vext.pygtk',

    version='0.1.2',

    description='Use system python packages in a virtualenv',
    long_description=long_description,

    url='https://github.com/stuaxo/vext',

    author='Stuart Axon',
    author_email='stuaxo2@yahoo.com',

    license='MIT',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: MIT License',

        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
    ],

    # What does your project relate to?
    keywords='virtualenv pygtk vext',

    install_requires=["vext"],

    # If there are data files included in your packages that need to be
    # installed, specify them here.  If using Python 2.6 or less, then these
    # have to be included in MANIFEST.in as well.
    #package_data={
    #    'sample': ['package_data.dat'],
    #},

    # Install pygtk vext
    data_files=[
        (os.path.join(site_packages_path, 'vext/specs'), ['pygtk.vext'])
    ],
)
