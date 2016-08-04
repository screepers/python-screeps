try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

config = {
    'description': 'Screeps API',
    'author': 'dzhu, tedivm',
    'url': 'https://github.com/screepers/screeps-api',
    'download_url': 'https://github.com/screepers/screeps-api/releases',
    'author_email': 'tedivm@tedivm.com',
    'version': '0.2',
    'install_requires': [
        'nose', 
        'requires', 
        'requests>=2.10.0,<3',
        'websocket-client'
        ],
    'packages': ['screepsapi'],
    'scripts': [],
    'name': 'screepsapi'
}

setup(**config)
