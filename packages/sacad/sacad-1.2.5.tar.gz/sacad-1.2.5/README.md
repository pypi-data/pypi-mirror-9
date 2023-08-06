SACAD
=====
Smart Automatic Cover Art Downloader
------------------------------------

[![Latest Version](https://pypip.in/version/sacad/badge.svg?style=flat)](https://pypi.python.org/pypi/sacad/)
[![Tests Status](https://img.shields.io/travis/desbma/sacad/master.svg?label=tests&style=flat)](https://travis-ci.org/desbma/sacad)
[![Coverage](https://img.shields.io/coveralls/desbma/sacad/master.svg?style=flat)](https://coveralls.io/r/desbma/sacad?branch=master)
[![Supported Python versions](https://pypip.in/py_versions/sacad/badge.svg?style=flat)](https://pypi.python.org/pypi/sacad/)
[![License](https://pypip.in/license/sacad/badge.svg?style=flat)](https://pypi.python.org/pypi/sacad/)

SACAD is a multi platform command line tool to download album covers without manual intervention, ideal for integration in scripts, audio players, etc.


## Features

* Can target specific image size
* Support JPEG and PNG formats
* Currently support 4 cover sources:
    * Last.fm
    * Google Images
    * ecover.to
    * Amazon.com
* Smart sorting algorithm to select THE best cover for a given query, using several factors: source reliability, image format, image size, image similarity with reference cover, etc.
* Automatically crunch images with optipng or jpegoptim (can save 30% of filesize without any loss of quality, great for portable players)
* Cache search results locally for faster future search
* Do everything to avoid getting blocked by the sources: hide user-agent and automatically take care of rate limiting
* Automatically convert/resize image if needed
* Multiplatform (Windows/Mac/Linux)

SACAD is designed to be robust and be executed in batch of thousands of queries:

* HTML parsing is done without regex but with the LXML library, which is faster, and more robust to page changes
* When the size of an image reported by a source is not reliable (ie. Google Images), automatically download the first KB of the file to get its real size from the file header
* Use multithreading when relevant, to speed up processing


## Installation

**SACAD needs Python >= 3.3**.

### From PyPI (with PIP)

1. If you don't already have it, [install pip](http://www.pip-installer.org/en/latest/installing.html) for Python 3 (not needed if you are using Python >= 3.4)
2. Install SACAD: `pip3 install sacad`

### From source

1. If you don't already have it, [install setuptools](https://pypi.python.org/pypi/setuptools#installation-instructions) for Python 3
2. Clone this repository: `git clone https://github.com/desbma/sacad`
3. Install SACAD: `python3 setup.py install`

### Standalone Windows executable

Windows users can also download a standalone binary which does not require Python:

* [7z archive](https://dl.dropboxusercontent.com/u/70127955/sacad_latest_win.7z)
* [auto extractible](https://dl.dropboxusercontent.com/u/70127955/sacad_latest_win.exe)

#### Optional

Additionnaly, if you want to benefit from image crunching (lossless recompression):

* Install [optipng](http://optipng.sourceforge.net/)
* Install [jpegoptim](http://freecode.com/projects/jpegoptim)

On Ubuntu and other Debian derivatives, you can install both with `sudo apt-get install optipng jpegoptim`.

Note that depending of the speed of your CPU, crunching may significantly slow down processing as it is very CPU intensive (especially for PNG files).


## Command line usage

To download the cover of _Master of Puppets_ from _Metallica_, to the file `AlbumArt.jpg`, targetting ~ 600x600 pixel resolution: `sacad 'metallica' 'master of puppets' 600 AlbumArt.jpg`.

Run `sacad -h` to get full command line reference.


## Limitations

* Only supports front covers


## Adding cover sources

Adding a new cover source is very easy if you speak Python, you need to inherit the `CoverSource` class and implement the following methods:

* `getSearchUrl(self, album, artist)`
* `updateHttpHeaders(self, headers)`
* `parseResults(self, api_data)`

See comments in the code for more information.


## License

[Mozilla Public License Version 2.0](https://www.mozilla.org/MPL/2.0/)
