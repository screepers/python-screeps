# Always prefer setuptools over distutils
from setuptools import setup, find_packages

try:
    import pypandoc
    long_description = pypandoc.convert('README.md', 'rst')
except(IOError, ImportError):
    long_description = open('README.md').read()


version = '0.4.2'
setup(
  name = 'screepsapi',
  version = version,
  packages=find_packages(),

  description = 'Screeps Unofficial Client for the Unofficial API',
  long_description=long_description,
  python_requires='>=2',

  author = 'Robert Hafner, dzhu',
  author_email = 'tedivm@tedivm.com',
  url = 'https://github.com/screepers/screeps-api',
  download_url = "https://github.com/screepers/screeps-api/archive/v%s.tar.gz" % (version),
  keywords = 'screeps api',

  classifiers = [
    'Development Status :: 4 - Beta',
    'License :: OSI Approved :: MIT License',
    'Intended Audience :: Developers',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 2',
  ],

  install_requires=[
    'nose',
    'requires',
    'requests>=2.10.0,<3',
    'websocket-client'
  ],

  extras_require={
    'dev': [
      'pypandoc',
      'twine',
      'wheel'
    ],
  },

)
