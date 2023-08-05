try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup
import os
import sys
import shout

if sys.argv[-1] == 'cheeseit!':
    os.system('python setup.py sdist upload')
    sys.exit()

with open("README.rst") as f:
    readme = f.read()

setup(
    name=shout.__title__,
    version=shout.__version__,
    description=shout.__description__,
    long_description=readme,
    author=shout.__author__,
    author_email=shout.__email__,
    url=shout.__url__,
    license="MIT",
    py_modules=['shout'],
    classifiers=(
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        "Topic :: Software Development :: Libraries :: Python Modules",
    ),
)
