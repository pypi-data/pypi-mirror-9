from distutils.core import setup

VER = '0.2.0'

setup(
    name='panns',
    version=VER,
    packages=['panns',],
    description = 'Python Approximate Nearest Neighbor / Neighbour Search',
    #long_description=open('README.md').read(),
    author = 'Liang Wang',
    author_email = 'ryanrhymes@gmail.com',
    url = 'https://github.com/ryanrhymes/panns',
    download_url = 'https://github.com/ryanrhymes/panns/archive/%s.zip' % VER,
    keywords = ['k-nn', 'knn', 'nearest neighbor', 'nearest neighbor search' 'approximate nearest neighbor', 'approximate neighbor search',
                'nearest neighbour', 'nearest neighbour search' 'approximate nearest neighbour', 'approximate neighbour search',
                'high demensional search', 'high-dimension data', 'LSH', 'locality sensitive hashing', 'random projection'],
    classifiers = [],
    license='GNU LGPL v2.1',

)
