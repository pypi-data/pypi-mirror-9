from distutils.core import setup
from setuptools import setup, find_packages  # Always prefer setuptools over distutils
setup(
  name = 'PyMissingData',
  packages=find_packages(exclude=['contrib', 'docs', 'tests*']),
  version = '1.0.4',
  description = 'An approach based on Bayesians Networks to fill missing values',
  long_description = 'To take full advantage of all information available, it is best to use as many available catalogs as possible. For example, adding u-band or X-ray information while classifying quasars based on their variability is highly likely to improve the overall performance.\r\nBecause these catalogs are taken with different instruments, bandwidths, locations, times, etc., the intersection of these catalogs is smaller than any single catalog; thus, the resulting multi-catalog contains missing values. Traditional classification methods cannot deal with the resulting missing data problem because to train a classification model it is necessary to have all features for all training members.\r\nPyMissingData allows you to perform inference to predict missing values given the observed data and dependency relationships between variables.',
  author = 'Augusto Sandoval',
  author_email = 'augustocsandoval@gmail.com',
  # Choose your license
  license='Harvard University',
  url = 'http://arsandov.github.io/PyMissingData',
  download_url = 'https://github.com/arsandov/PyMissingData/releases/tag/1.0.4',
  keywords = ['Missing Values', 'Machine Learning', 'Bayesian Networks'],

    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: Astronomy',
        'Topic :: Software Development :: Build Tools',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7'
    ],
)

