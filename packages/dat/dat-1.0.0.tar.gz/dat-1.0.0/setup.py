from setuptools import setup, find_packages
from dat import __version__

import os


def file_name(rel_path):
    dir_path = os.path.dirname(__file__)
    return os.path.join(dir_path, rel_path)


setup(
    author="Anthony Almarza",
    author_email="anthony.almarza@gmail.com",
    name="dat",
    packages=find_packages(exclude=["tests*", ]),
    version=__version__,
    url="https://github.com/anthonyalmarza/dat",
    download_url=(
        "https://github.com/anthonyalmarza/dat/tarball/"
        "v" + __version__
    ),
    license="MIT",
    description="A thin orm for pymongo",
    long_description="This is a test description",
    classifiers=[
        'Development Status :: 4 - Beta',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP',
    ],
    keywords=["mongo", "pymongo", "orm-ish", "data", "nosql"],
    install_requires=['pymongo', ],
    extras_require={
        'dev': ['ipdb', 'mongomock', 'mock'],
    }
)
