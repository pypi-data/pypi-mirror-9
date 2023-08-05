import os
from setuptools import setup
import sys


# pip workaround
os.chdir(os.path.abspath(os.path.dirname(__file__)))


with open('README.rst') as fp:
    description = fp.read()
req = [
    'PyYAML',
    'rpaths>=0.8',
    'usagestats>=0.3']
if sys.version_info < (2, 7):
    req.append('argparse')
setup(name='reprounzip',
      version='0.6',
      packages=['reprounzip', 'reprounzip.unpackers',
                'reprounzip.unpackers.common', 'reprounzip.plugins'],
      entry_points={
          'console_scripts': [
              'reprounzip = reprounzip.main:main'],
          'reprounzip.unpackers': [
              'info = reprounzip.pack_info:setup_info',
              'showfiles = reprounzip.pack_info:setup_showfiles',
              'graph = reprounzip.unpackers.graph:setup',
              'installpkgs = reprounzip.unpackers.default:setup_installpkgs',
              'directory = reprounzip.unpackers.default:setup_directory',
              'chroot = reprounzip.unpackers.default:setup_chroot']},
      namespace_packages=['reprounzip', 'reprounzip.unpackers'],
      install_requires=req,
      extras_require={
          'all': ['reprounzip-vagrant>=0.6', 'reprounzip-docker>=0.6']},
      description="Linux tool enabling reproducible experiments (unpacker)",
      author="Remi Rampin, Fernando Chirigati, Dennis Shasha, Juliana Freire",
      author_email='reprozip-users@vgc.poly.edu',
      maintainer="Remi Rampin",
      maintainer_email='remirampin@gmail.com',
      url='http://vida-nyu.github.io/reprozip/',
      long_description=description,
      license='BSD',
      keywords=['reprozip', 'reprounzip', 'reproducibility', 'provenance',
                'vida', 'nyu'],
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Intended Audience :: Science/Research',
          'License :: OSI Approved :: BSD License',
          'Topic :: Scientific/Engineering',
          'Topic :: System :: Archiving'])
