from distutils.core import setup
#from setuptools import setup
from selectx import __version__ as VERSION
PACKAGE = "slectx"
NAME = "SelectX"
DESCRIPTION = "SelectX - easy eXtendable text editor for developers writed on Python. Licensed by GPL3."
LONG_DESCRIPTION = '''SelectX - easy eXtendable text editor for developers writed on Python. Based on "Explicit is better than implicit" philosophy. Licensed by GPL3.'''
AUTHOR = "1_0"
AUTHOR_EMAIL = "1_0@usa.com"
URL = r"https://github.com/1-0/SelectX"

setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    license="GPL3",
    url=URL,
    #install_requires = ['PySide>=1.0'],
    scripts = ['selectx.py'],
    #packages=[PACKAGE,],
    #packages=find_packages(exclude=["tests.*", "tests"]),
    #package_data=find_package_data(
#			PACKAGE,
#			only_in_packages=False
#	  ),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: X11 Applications :: Qt",
        "Intended Audience :: Developers",
        'Intended Audience :: End Users/Desktop',
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Text Editors",
    ],
    zip_safe=False,
)

