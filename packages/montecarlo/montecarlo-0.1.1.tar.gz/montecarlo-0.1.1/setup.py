try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

with open('README.md') as file:
    long_description = file.read()

setup(
  name = 'montecarlo',
  packages = ['montecarlo'],
  version = '0.1.1',
  description = 'A small Python library for creating simple Monte Carlo simulations.',
  long_description=long_description,
  author = 'Christopher Su',
  author_email = 'chris+gh@christopher.su',
  url = 'https://github.com/csu/pymontecarlo',
  download_url = 'https://github.com/csu/pymontecarlo/archive/master.zip',
)