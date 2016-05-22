try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

config = {
    'description': 'Screeps API',
    'author': 'dzhu, tedivm',
    'url': 'https://github.com/tedivm/screeps-api',
    'download_url': 'https://github.com/tedivm/screeps-api/releases',
    'author_email': 'tedivm@tedivm.com',
    'version': '0.1',
    'install_requires': ['nose', 'requires'],
    'packages': ['screeps'],
    'scripts': [],
    'name': 'screeps'
}

setup(**config)
