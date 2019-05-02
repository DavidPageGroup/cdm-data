"""Package definition and install configuration for `cdmdata`"""

# Copyright (c) 2019 Aubrey Barnard.
#
# This is free, open software licensed under the [MIT License](
# https://choosealicense.com/licenses/mit/).


import setuptools

import cdmdata


# Extract the short and long descriptions from the documentation
_desc_paragraphs = cdmdata.__doc__.strip().split('\n\n')
# Make sure to keep the short description to a single line
_desc_short = _desc_paragraphs[0].replace('\n', ' ')
# Include all the package documentation in the long description except
# for the first and last paragraphs which are the short description and
# the copyright notice, respectively
_desc_long = '\n\n'.join(_desc_paragraphs[1:-2])


# Define package attributes
setuptools.setup(

    # Basics
    name='cdmdata',
    version=cdmdata.__version__,
    url='https://github.com/DavidPageGroup/cdm-data/tree/master/pypkg',
    license='MIT',
    author='Aubrey Barnard',
    #author_email='',

    # Description
    description=_desc_short,
    long_description=_desc_long,
    keywords=[
        'data processing',
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Scientific/Engineering :: Information Analysis',
        'Topic :: Utilities',
    ],

    # Requirements
    python_requires='~= 3.4',
    install_requires=[
        'esal ~= 0.3.0',
    ],

    # API
    packages=setuptools.find_packages(),

)
