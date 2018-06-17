from os.path import dirname, join, abspath
from setuptools import setup, find_packages

ROOT_DIR = dirname(abspath(__file__))

setup(
    packages=find_packages(where=join(ROOT_DIR, 'src')),
    package_dir={'gramedia': 'src/gramedia'},

    project_urls={
        'Documentation': 'https://gdn-python-common.rtfd.io/',
        'Source': 'https://github.com/gramedia-digital-nusantara/python-common',
        'Tracker': 'https://github.com/gramedia-digital-nusantara/python-common/issues',
    },
)
