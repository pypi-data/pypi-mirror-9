
"""
renderthreads
==========================================

Package that enables easy command-line
multithreaded rendering for Nuke.
"""

# Import
# ------------------------------------------------------------------
from setuptools import setup
from setuptools import find_packages

# Setup
# ------------------------------------------------------------------
setup(name = 'renderthreads',
      version = '0.2.2',
      description = 'Package that enables easy command-line multithreaded rendering for Nuke.',
      url = 'https://github.com/timmwagener/renderthreads',
      author = 'Timm Wagener',
      author_email = 'wagenertimm@gmail.com',
      license = 'MIT',
      keywords = 'Foundy TheFoundry Nuke Pipeline Compositing Filmakademie Timm Wagener Multithreading Commandline Rendering',
      packages = find_packages(),
      include_package_data = True,
      zip_safe = False)
