import sys
sys.path.append('.')
import neurio

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
  name = 'neurio',
  packages = ['neurio'],
  version = str(neurio.__version__),
  description = 'Neurio energy sensor and appliance automation API library',
  author = 'Jordan Husney',
  author_email = 'jordan.husney@gmail.com',
  url = 'https://github.com/jordanh/neurio-python',
  download_url = 'https://github.com/jordanh/neurio-python/tarball/0.2.2',
  keywords = ['neurio', 'iot', 'energy', 'sensor', 'smarthome', 'automation'],
  classifiers = [],
  install_requires = ['requests'],
)
