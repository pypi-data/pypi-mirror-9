"""Setup Script """
from setuptools import setup, find_packages
import sys
sys.path.append('./tests')

__author__ = 'KAWASAKI Yasukazu (yakawa)'
__email__ = 'kawasaki@dev.kawa1128.jp'
__version__ = '0.0.1.2'


setup(
  name='PyJSONConfigParser',
  version=__version__,
  description='ConfigParser using json format',
  author=__author__,
  author_email=__email__,
  long_description=open('README.md').read(),
  license='MIT',
  keywords=['JSON', 'config', 'ConfigParser'],
  url='https://github.com/yakawa/PyJSONConfigParser',
  install_requires=[
    'pytz',
  ],
  tests_require=[
  ],
  package_dir={'': 'src'},
  packages=find_packages('src'),
  include_package_data=True,
  test_suite='testJSONConfigParser.suite',
  classifiers=[
    'Programming Language :: Python',
    'Programming Language :: Python :: 3',
    'Operating System :: OS Independent',
    'Development Status :: 3 - Alpha',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: MIT License',
    'Topic :: Software Development :: Libraries :: Python Modules',
    'Topic :: Utilities',
  ],
)
