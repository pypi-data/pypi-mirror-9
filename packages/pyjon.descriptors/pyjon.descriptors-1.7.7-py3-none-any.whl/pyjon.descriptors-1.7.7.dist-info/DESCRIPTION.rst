Introduction
============

pyjon.descriptors is a standardized way of describing a file and
to get a generator that yields python objects from that file to your program.

The yielded python objects contain attributes that are defined in an
XML schema and their types and content are garanteed by pyjon.descriptors.

The provided readers are `csv`, `xml` (specific schema) and `fixedlen`
readers but more can be written easily.

Running the tests
=================

install the tests requirements::

  $ pip install --upgrade tox

the run the test suite and generate the coverage report with
the following command::

  $ tox

you should now have a directory called `coverage_html_report` with a file
named `index.html` inside


Python 3 compatibility
======================

pyjon.descriptors should work just fine on Python 3.

Note about upgrading from previous versions: "dirty" XML files (with custom "rc" tags) are no
longer supported.

Contributors
============

in oder of appeareance on the project

  - Florent Aide
  - Jonathan Schemoul
  - Jerôme Collette
  - Mathieu Bridon
  - Emmanuel Cazenave
  - Houzéfa Abbasbhay


