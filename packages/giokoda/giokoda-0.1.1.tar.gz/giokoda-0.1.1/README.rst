This is a `Python <http://python.org>`_ based utility for geocoding csv files
using various online geocoding service.

*************
Installation
*************

Installation using `pip <https://pip.pypa.io>`_
================================================

::

    pip install giokoda

Installation from source
========================
Download the source code from github, Example 

::

    git clone https://github.com/WorldBank-Transport/giokoda.git

Install the module and its dependancies

::

    cd giokoda
    python setup.py install


******
Usage
******

This utility can be used as a Python module or as an executable script.

Using as python module
=======================

Basic example::

    import giokoda
    giokoda.geocode_csv('input.csv')

The above code will try to goecode the provided `'input.csv'` file and write
its output to `'input.csv-geocoded.csv'`

A `geocode_csv` function can geocode entities from a provided input csv file
and write results to a csv file.

It also returns a dictionary containing error, success and total count of
geocoded rows.

General syntax::

    geocode_csv('input/file.csv', **kwargs)

Required parameter
------------------

    `infile`, *(filepath/str)*
        path to a csv file to geocode.

Optional keyword arguments (`**kwargs`)
---------------------------------------
    `outfile`, (filepath/str)
        path to file to write output csv
    
    `service`, *(str)*, default: `'nominatim'`.
        Name of a geocoding service to use. This can be a name of any geocoding
        service that is supported by
        `geopy <http://geopy.readthedocs.org/en/latest/>`_.

    `query_column`, *(str)*, default: `'name'`
        Name of a column containg text to geocode.

    `query_columns` *(list)*: default: `[]`. A list of a columns
    to be combined in order to produce a text to geocode.

    `service_kwargs`, *(dict)*
        Optional keyword arguments for initialization of geocoding service.

    `delimiter` *(str)*: default: `','`, A one-character string used to
    separate fields.

    `quotechar` *(str)*: default: `'"'`, A one-character string used to
    quote fields containing special characters in a csv file, such as
    the delimiter or quotechar, or which contain new-line characters.

Return
------

`geocode_csv()` returns a dictionary of success, error and total count::
  
    {
        'total': 0,
        'success': 0,
        'error': 0
    }

Using an executable script
==========================

* Run `geocode_csv` via command line interface.

Example::

    geocode_csv /input/file.csv

or including a api key::

    geocode_csv --service <SERVICE-NAME> --params '{"api_key": "<YOUR-API-KEY>"}' /input/file.csv

General usage::

    geocode_csv [-h] [-o OUTPUT] [-s SERVICE] [-c COLUMN] [-p PARAMS] input

Required argument
------------------
    `input`
        Full path to csv file to geocode

`Optional arguments`
---------------------

    `-h, --help`
        show this help message and exit

    `-o OUTPUT, --output OUTPUT`
        Full path to output file

    `-s SERVICE, --service SERVICE`
        Geocoding service name, example arcgis, baidu, google, googlev3, geocoderdotus,
        geonames, yahoo, placefinder, opencage, openmapquest, mapquest, liveaddress,
        navidata, nominatim, geocodefarm, what3words, yandex and ignfrance

    `-c [COLUMN [COLUMN ...]], --column [COLUMN [COLUMN ...]]`
        Name(s) for column(s) containing text content to geocode.
        Multiple column names should be separated by white space.

    `-p PARAMS, --params PARAMS`
        Keyword arguments for geocoding service initialization presented as
        json object

    `-d DELIMITER, --delimiter DELIMITER`
        A one-character string used to separate fields in a csv file

    `-q QUOTECHAR, --quotechar QUOTECHAR`
        A one-character string used to
        quote fields containing special characters in a csv file, such as
        the delimiter or quotechar, or which contain new-line characters.
