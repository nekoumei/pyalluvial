from setuptools import setup, find_packages
from os import path
import re

root_dir = path.abspath(path.dirname(__file__))
package_name = 'pyalluvial'

try:
    with open('README.md') as f:
        readme = f.read()
except IOError:
    readme = ''


def _requires_from_file(filename):
    return open(filename).read().splitlines()

setup(
    name=package_name,
    version='0.0.0',
    url='https://github.com/nekoumei/pyalluvial',
    author='nekoumei',
    author_email='nekoumei@gmail.com',
    maintainer='nekoumei',
    maintainer_email='nekoumei@gmail.com',
    description='Plotting Alluvial Plot',
    long_description=readme,
    packages=find_packages(),
    install_requires=_requires_from_file('requirements.txt'),
    license="MIT",
    classifiers=[
        'Programming Language :: Python :: 3.6',
        'License :: OSI Approved :: MIT License',
        'Development Status :: 4 - Beta',
        'Environment :: MacOS X',
        'Topic :: Scientific/Engineering :: Artificial Intelligence'
    ]
)