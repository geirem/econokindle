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
This application requires the [Kindle Gen](https://www.amazon.com/gp/feature.html?ie=UTF8&docId=1000765211) application,
which must be downloaded and installed separately.

## How to Use
The application runs under the [Pipenv](https://docs.pipenv.org/en/latest/) Python 3.7 virtual environment.  To use the
application, install Python and Pipenv and run the `src/main/python/main.py` script.  A brief help page shows parameters
that can be changed from their defaults.  By default, it assumes that:
* `kindlegen` is installed in `$HOME/bin/`
* your Kindle is mounted under `/Kindle/documents/`

## Bug Reports
Please submit bug reports or pull requests through GitHub.
