from codecs import open as codecs_open
from setuptools import setup, find_packages


# Get the long description from the relevant file
with codecs_open('README.rst', encoding='utf-8') as f:
    long_description = f.read()


setup(name='gribnormalize',
      version='0.0.1',
      description=u"Utility functions for handling quirks of weather data rasters in grib2 format",
      long_description=long_description,
      classifiers=[],
      keywords='',
      author=u"Damon Burgett",
      author_email='damon@mapbox.com',
      url='https://github.com/mapbox/grib-normalizer',
      license='MIT',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'click',
          'rasterio',
          'scipy'
      ],
      extras_require={
          'test': ['pytest'],
      },
      entry_points="""
      [console_scripts]
      gribnormalize=gribnormalize.scripts.cli:cli
      """
      )
