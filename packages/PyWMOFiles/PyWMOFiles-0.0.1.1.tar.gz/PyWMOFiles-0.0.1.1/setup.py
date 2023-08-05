"""Setup Script """
from setuptools import setup, find_packages
import sys
sys.path.append('./tests')

__author__ = 'KAWASAKI Yasukazu (yakawa)'
__email__ = 'kawasaki@dev.kawa1128.jp'
__version__ = '0.0.1.1'

setup(
  name='PyWMOFiles',
  version=__version__,
  description='Files defined by WMO  read module',
  author=__author__,
  author_email=__email__,
  long_description=open('README.md').read(),
  license='MIT',
  keywords=['BUFR', 'WMO', 'Parser'],
  url='https://github.com/yakawa/PyWMOFiles',
  install_requires=[
  ],
  tests_require=[
  ],
  package_dir={'': 'src'},
  packages=find_packages('src'),
  include_package_data=True,
  package_data={'': ['tables/*.json']},
  data_files=[('', 'README.md'),],
  test_suite='testPyWMOFiles.suite',
  classifiers=[
    'Development Status :: 3 - Alpha',
    'Intended Audience :: Science/Research',
    'License :: OSI Approved :: MIT License',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Programming Language :: Python :: 3',
    'Topic :: Software Development :: Libraries :: Python Modules',
    'Topic :: Scientific/Engineering :: Atmospheric Science'
  ],
)
