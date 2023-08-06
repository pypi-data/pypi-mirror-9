from setuptools import setup
from setuptools import find_packages

setup(
    name='GeobricksRasterCorrelation',
    version='0.1.1',
    author='Simone Murzilli; Guido Barbaglia',
    author_email='geobrickspy@gmail.com',
    packages=find_packages(),
    license='LICENSE.txt',
    long_description=open('README.md').read(),
    description='Geobricks library to correlate two raster and create statistics and scatter charts.',
    install_requires=[
        'watchdog',
        'flask',
        'flask-cors',
        'brewer2mpl',
        'PySal',
        'numpy',
        'scipy',
        'GeobricksCommon',
    ],
    url='http://pypi.python.org/pypi/GeobricksRasterCorrelation/',
    keywords=['geobricks', 'processing', 'raster', 'gis', 'gdal', 'correlation', 'raster correlation', 'highcharts']
)
