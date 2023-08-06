=======
pyicane
=======
**pyicane** is a Python wrapper for the Statistical Office of
Cantabria's (ICANE) metadata restful API. This module parses ICANE's json data
and metadata into Python objects and common data structures such as Pandas
dataframes [1]_. All ICANE's API classes and methods are covered; also,
time-series data can be downloaded into a Python Pandas dataframe structure.

pyicane is written and maintained by `Miguel Expósito Martín \
<https://twitter.com/predicador37>`_ and is distributed under the Apache 2.0 \
License (see LICENSE file).

.. [1] http://pandas.pydata.org for Python Data Analysis Library information

Installation
============

pyicane requires pandas and requests packages. For installation::

    pip install pyicane

Usage
=====

Get a list of categories
------------------------
Typical usage often looks like this::

    from pyicane import pyicane

    categories = pyicane.Category.find_all()
    print categories

Get Time Series Data in a Dataframe
-----------------------------------
Conversion to dataframe is a useful feature::

    from pyicane import pyicane

    time_series = pyicane.TimeSeries.get('census-series-1900-2001')
    print time_series.data_as_dataframe()

Get Time Series Metadata in a Dataframe
---------------------------------------
Let's check the most relevant metadata::

    from pyicane import pyicane

    time_series = pyicane.TimeSeries.get('census-series-1900-2001')
    print time_series.metadata_as_dataframe()

Get last updated data
---------------------
Which was the last ICANE's API data update::

    from pyicane import pyicane

    print pyicane.Data.get_last_updated()
