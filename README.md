![actions](https://github.com/geirem/econokindle/workflows/Python%20application/badge.svg?branch=master)

# Economist Kindle Formatter.
## Purpose
The purpose of this application is to read The Economist on your personal Kindle device.  It downloads the latest
edition to a mounted Kindle device.

It is developed and tested using a Mac with Kindle Previewer 3 and Kindle Paperwhite.  Testing for other platforms
has not been done, but feel free to create a PR for your OS or Kindle version.

## License
The application is released under [Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International](https://creativecommons.org/licenses/by-nc-sa/4.0/).   This license does not extend to content processed by the application.

## Disclaimer
#### Trademarked Terms
Trademarked terms used in this application are used in good faith, according to the ["fair use policy."](https://www.inta.org/TrademarkBasics/FactSheets/Pages/Fair-Use-of-TrademarksNL.aspx)

#### Usage Policy
Use of the application must conform to [The Economist's terms of use](https://www.economist.com/legal/terms-of-use).

## Dependencies
This application is written in the latest version of Python, currently 3.8.  It uses no libraries not
available on [PyPI](pypi.org/), except the converter application described below.

To convert from HTML to MOBI, it requires the [KindleGen](https://www.amazon.com/gp/feature.html?ie=UTF8&docId=1000765211), or the [Calibre](https://calibre-ebook.com/)
applications.  Either application must be dowloaded and installed separately.

As KindleGen is not supported on MacOS Catalina or newer, for this platform you must use Calibre.


## How to Use
To use this application:
* Download [EconoKindle](https://github.com/geirem/econokindle) from GitHub.
* Install the latest version of [Python](https://www.python.org/downloads/).
* Create a local virtual environment (recommended):
    * `python3 -m venv .venv`
    * `source .venv/bin/activate`
* Install the Python dependencies from PyPI
    * `pip3 install -r requirements.txt`
* Install the converter application (Kindlegen or Calibre) according to the
vendor's instructions (see above).
* Run this application as `python3 main.py`

## Bug Reports
Please submit bug reports or pull requests through GitHub.
