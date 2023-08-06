import os
from setuptools import setup

from rosbag_metadata.config import VERSION

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

install_requires = [
    'netifaces',
    'GitPython',
    'PyYAML'
]

setup(
    name = "rosbag_metadata",
    version = VERSION,
    author = "Hordur K Heidarsson",
    author_email = "hordur@hordur.us",
    description = ("Tool for collecting and writing metadata to ROS "
                                   "bagfiles or to accompanying yaml files."),
    license = "MIT",
    install_requires=install_requires,
    keywords = "ros rosbag metadata",
    url = "http://rosbag-metadata.readthedocs.org/",
    packages=['rosbag_metadata'],
    long_description=read('README.md'),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: MIT License",
    ],
    entry_points={
        'console_scripts': [
            'rosbag_metadata = rosbag_metadata.rosbag_metadata:main'
        ],
    },
)
