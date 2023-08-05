Kantonzugpdf
============

A library to create PDF reports for the Canton of Zug

Usage
-----

Create a subclass and provide ``populate``::

    from kantonzugpdf import ReportZug
    from reportlab.lib.units import cm

    class MyReport(ReportZug):

        def populate(self):
            self.title = u'My Report'
            self.adjust_style()

            # The first page contains the title and table of contents
            self.pdf.h(self.title)
            self.pdf.table_of_contents()
            self.pdf.pagebreak()

            # The second page has some titles and paragraphs
            self.pdf.h1(u'Title')
            self.pdf.h2(u'Subtitle')
            self.pdf.p(u'This is a paragraph.')
            self.pdf.h2(u'Another subtitle')
            self.pdf.p(u'This is another paragraph.')
            self.pdf.p(u'And again, a paragraph.')
            self.pdf.pagebreak()

            # The third page contains a table
            self.pdf.h1(u'Here comes the table')
            self.pdf.table([[u'a', u'b'], [u'c', u'd']], [5*cm, 10*cm])
            self.pdf.spacer()
            self.pdf.p(u'Above we see a table.')

call ``build``::

    TestReport().build()

Run the Tests
-------------

Install tox and run it::

    pip install tox
    tox

Limit the tests to a specific python version::

    tox -e py27

Conventions
-----------

Kantonzugpdf follows PEP8 as close as possible. To test for it run::

    tox -e pep8

Kantonzugpdf uses `Semantic Versioning <http://semver.org/>`_

Build Status
------------

.. image:: https://travis-ci.org/seantis/kantonzugpdf.png
  :target: https://travis-ci.org/seantis/kantonzugpdf
  :alt: Build Status

Coverage
--------

.. image:: https://coveralls.io/repos/seantis/kantonzugpdf/badge.png?branch=master
  :target: https://coveralls.io/r/seantis/kantonzugpdf?branch=master
  :alt: Project Coverage

Latests PyPI Release
--------------------
.. image:: https://pypip.in/v/kantonzugpdf/badge.png
  :target: https://crate.io/packages/kantonzugpdf
  :alt: Latest PyPI Release

License
-------
kantonzugpdf is released under GPLv2
