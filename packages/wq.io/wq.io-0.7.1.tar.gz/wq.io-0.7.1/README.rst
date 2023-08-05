|wq.io|

`wq.io <http://wq.io/wq.io>`__ is a Pythonic library for consuming
(input), iterating over, and generating (output) external data resources
in various formats. wq.io facilitates interoperability between the `wq
framework <http://wq.io/>`__ and other systems and formats.

wq.io is `designed to be customized <http://wq.io/docs/custom-io>`__,
with a `base class <http://wq.io/docs/base-io>`__ and modular mixin
classes that handle `loading <http://wq.io/docs/loaders>`__,
`parsing <http://wq.io/docs/parsers>`__, and
`mapping <http://wq.io/docs/mappers>`__ external data to a convenient
API.

    Coincidentally, http://wq.io is also the URL for the website
    describing the wq framework as a whole. The documentation for wq.io
    (the library) is available on wq.io (the website) at
    http://wq.io/wq.io.

|Build Status| |PyPI Package|

Tested on Python 2.7 and 3.4.

Getting Started
---------------

.. code:: bash

    # Basic install
    pip3 install wq.io

    # Alternatively, install the wq metapackage if using together with wq.app and/or wq.db:
    pip3 install wq

    # To enable wq.io's GIS support
    pip3 install geopandas # includes Shapely & Fiona

    # To enable wq.io's Excel write support
    pip3 install xlwt # xls support (use xlwt-future for Python 3)
    pip3 install xlsxwriter # xlsx support
    # (xls/xlsx read support is enabled by default)

See `the wq documentation <http://wq.io/docs/>`__ for more information.

Features
--------

wq.io provides a general purpose API for loading, iterating over, and
writing tabular datasets. The basic idea is to avoid needing to remember
the unique usage of e.g.
`csv <https://docs.python.org/3/library/csv.html>`__,
`xlrd <http://www.python-excel.org/>`__, or
`xml.etree <https://docs.python.org/3/library/xml.etree.elementtree.html>`__
every time one needs to work with external data. Instead, wq.io
abstracts these libraries into a consistent interface that works as an
`iterable <https://docs.python.org/3/glossary.html#term-iterable>`__ of
`namedtuples <https://docs.python.org/3/library/collections.html#collections.namedtuple>`__.
Whenever possible, the field names for a dataset are automatically
determined from the source file, e.g. the column headers in an Excel
spreadsheet.

.. code:: python

    from wq.io import ExcelFileIO
    data = ExcelFileIO(filename='example.xls')
    for row in data:
        print row.name, row.date

wq.io provides a number of built-in classes like the above, including a
``CsvFileIO``, ``XmlFileIO``, and ``JsonFileIO``. There is also a
convenience function, ``load_file()``, that attempts to automatically
determine which class to use for a given file.

.. code:: python

    from wq.io import load_file
    data = load_file('example.csv')
    for row in data:
        print row.name, row.date

All of the included ``*FileIO`` classes support both reading and writing
to external files, though write support for Excel files requires
additional libraries (`xlwt <http://www.python-excel.org/>`__ and
`xlsxwriter <https://xlsxwriter.readthedocs.org/>`__) that aren't listed
as dependencies.

Network Client
~~~~~~~~~~~~~~

wq.io also provides network-capable equivalents of each of the above
classes, to facilitate loading data from third party webservices.

.. code:: python

    from wq.io import JsonNetIO
    class WebServiceIO(JsonNetIO):
        url = "http://example.com/api"
        
    data = WebServiceIO(params={'type': 'all'})
    for row in data:
        print row.timestamp, row.value

The powerful `requests <http://python-requests.org/>`__ library is used
internally to load data over HTTP.

Pandas Analysis
~~~~~~~~~~~~~~~

When `Pandas <http://pandas.pydata.org/>`__ is installed, the
``as_dataframe()`` method on wq.io classes can be used to create a
`DataFrame <http://pandas.pydata.org/pandas-docs/stable/generated/pandas.DataFrame.html>`__,
enabling more extensive analysis possibilities.

.. code:: python

    instance = WebServiceIO(params={'type': 'all'})
    df = instance.as_dataframe()
    print df.value.mean()

GIS Support
~~~~~~~~~~~

When `Fiona <https://github.com/Toblerity/Fiona>`__ and
`Shapely <https://github.com/Toblerity/Shapely>`__ are installed, wq.io
can also open and create shapefiles and other OGR-compatible geographic
data formats.

.. code:: python

    from wq.io import ShapeIO
    data = ShapeIO(filename='sites.shp')
    for id, site in data.items():
        print id, site.geometry.wkt

Extending wq.io
~~~~~~~~~~~~~~~

Each ``IO`` class is composed of mixin classes
(`loaders <http://wq.io/docs/loaders>`__,
`parsers <http://wq.io/docs/parsers>`__, and
`mappers <http://wq.io/docs/mappers>`__) that handle the various steps
of the process. By extending these mixin or the pre-mixed classes above,
it is straightforward to `extend wq.io <http://wq.io/docs/custom-io>`__
to support arbitrary formats. The `climata
library <https://github.com/heigeo/climata>`__ provides a number of
examples of custom ``IO`` classes for loading climate and hydrology
data.

.. |wq.io| image:: https://raw.github.com/wq/wq/master/images/256/wq.io.png
   :target: http://wq.io/wq.io
.. |Build Status| image:: https://travis-ci.org/wq/wq.io.svg?branch=master
   :target: https://travis-ci.org/wq/wq.io
.. |PyPI Package| image:: https://pypip.in/version/wq.io/badge.svg?style=flat
   :target: https://pypi.python.org/pypi/wq.io
