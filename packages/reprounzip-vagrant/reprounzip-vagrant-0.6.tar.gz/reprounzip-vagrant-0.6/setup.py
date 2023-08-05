import os
from setuptools import setup


# pip workaround
os.chdir(os.path.abspath(os.path.dirname(__file__)))


with open('README.rst') as fp:
    description = fp.read()
setup(name='reprounzip-vagrant',
      version='0.6',
      packages=['reprounzip', 'reprounzip.unpackers',
                'reprounzip.unpackers.vagrant'],
      entry_points={
          'reprounzip.unpackers': [
              'vagrant = reprounzip.unpackers.vagrant:setup']},
      namespace_packages=['reprounzip', 'reprounzip.unpackers'],
      install_requires=[
          'reprounzip>=0.6',
          'rpaths>=0.8',
          'paramiko',
          'scp'],
      description="Allows the ReproZip unpacker to create virtual machines",
      author="Remi Rampin, Fernando Chirigati, Dennis Shasha, Juliana Freire",
      author_email='reprozip-users@vgc.poly.edu',
      maintainer="Remi Rampin",
      maintainer_email='remirampin@gmail.com',
      url='http://vida-nyu.github.io/reprozip/',
      long_description=description,
      license='BSD',
      keywords=['reprozip', 'reprounzip', 'reproducibility', 'provenance',
                'vida', 'nyu', 'vagrant'],
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Intended Audience :: Science/Research',
          'License :: OSI Approved :: BSD License',
          'Topic :: Scientific/Engineering',
          'Topic :: System :: Archiving'])
