import glob
import os
from distutils.core import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = 'cnb-exchange-rate',
    packages = ['cnb_exchange_rate'],
    version = '0.1.1',
    description = 'Czech National Bank Exchange Rate Downloader',
    long_description = 'Python library for downloading exchange rates from the Czech National Bank.',
    license = 'MIT',
    author = 'Stepan Sojka',
    author_email = 'stepansojka@countermail.com',
    url = 'http://github.com/stepansojka/cnb-exchange-rate',
    keywords = ['CNB currency exchange'],
    package_dir={'': 'src'},
    install_requires = ['six'],
    py_modules=[splitext(basename(i))[0] for i in glob.glob('src/*.py')],
    classifiers = [
        'Topic :: Office/Business :: Financial',
        'Topic :: Utilities',
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3'
        ]
)
