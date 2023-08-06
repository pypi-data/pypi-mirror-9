Annotator Store
===============

This is a backend store for `Annotator <http://annotatorjs.org>`__.

The functionality can roughly be separated in two parts:

1. An abstraction layer wrapping Elasticsearch, to easily manage annotation
   storage. It features authorization to filter search results according to
   their permission settings.
2. A Flask blueprint for a web server that exposes an HTTP API to the annotation
   storage. To use this functionality, build this package with the ``[flask]``
   option.

Getting going
-------------

You'll need a recent version of `Python <http://python.org>`__ (Python 2 >=2.6
or Python 3 >=3.3) and `ElasticSearch <http://elasticsearch.org>`__ (>=1.0.0)
installed.

The quickest way to get going requires the ``pip`` and ``virtualenv``
tools (``easy_install virtualenv`` will get them both). Run the
following in the repository root::

    virtualenv pyenv
    source pyenv/bin/activate
    pip install -e .[flask]
    cp annotator.cfg.example annotator.cfg
    python run.py

You should see something like::

    * Running on http://127.0.0.1:5000/
    * Restarting with reloader...

If you wish to customize the configuration of the Annotator Store, make
your changes to ``annotator.cfg`` or dive into ``run.py``.

Additionally, the ``HOST`` and ``PORT`` environment variables override
the default socket binding of address ``127.0.0.1`` and port ``5000``.

Store API
---------

The Store API is designed to be compatible with the
`Annotator <http://okfnlabs.org/annotator>`__. The annotation store, a
JSON-speaking REST API, will be mounted at ``/api`` by default. See the
`Annotator
documentation <https://github.com/okfn/annotator/wiki/Storage>`__ for
details.

Running tests
-------------

We use ``nosetests`` to run tests. You can just
``pip install -e .[testing]``, ensure ElasticSearch is running, and
then::

    $ nosetests
    ......................................................................................
    ----------------------------------------------------------------------
    Ran 86 tests in 19.171s

    OK

Alternatively (and preferably), you should install
`Tox <http://tox.testrun.org/>`__, and then run ``tox``. This will run
the tests against multiple versions of Python (if you have them
installed).

Please `open an issue <http://github.com/openannotation/annotator-store/issues>`__
if you find that the tests don't all pass on your machine, making sure to include
the output of ``pip freeze``.


Changelog
=========

All notable changes to this project will be documented in this file. This
project endeavours to adhere to `Semantic Versioning`_.

.. _Semantic Versioning: http://semver.org/

Unreleased
----------

0.14.1
-----------------
- FIXED: Document plugin doesn't drop links without a type. The annotator
  client generates a typeless link from the document href. (#116)

- ADDED: the search endpoint now supports 'before' and 'after query parameters,
  which can be used to return annotations created between a specific time
  period.

0.14 - 2015-02-13
-----------------

-  ADDED: the search endpoint now supports 'sort' and 'order' query parameters,
   which can be used to control the sort order of the returned results.

-  FIXED: previously only one document was returned when looking for equivalent
   documents (#110). Now the Document model tracks all discovered equivalent
   documents and keeps each document object up-to-date with them all.

   BREAKING CHANGE: Document.get_all_by_uris() no longer exists. Use
   Document.get_by_uri() which should return a single document containing all
   equivalent URIs. (You may wish to update your index by fetching all documents
   and resaving them.)

-  FIXED: the search_raw endpoint no longer throws an exception when the
   'fields' parameter is provided.

0.13.2 - 2014-12-03
-------------------

-  Avoid a confusing error about reindexing when annotator is used as a
   library and not a standalone application (#107).

0.13.1 - 2014-12-03
-------------------

-  Reindexer can run even when target exists.

0.13.0 - 2014-12-02
-------------------

-  Slight changes to reindex.py to ease subclassing it.

0.12.0 - 2014-10-06
-------------------

-  A tool for migrating/reindexing elasticsearch (reindex.py) was added (#103).
-  The store returns more appropriate HTTP response codes (#96).
-  Dropped support for ElasticSearch versions before 1.0.0 (#92).
-  The default search query has been changed from a term-filtered "match all" to
   a set of "match queries", resulting in more liberal interpretations of
   queries (#89).
-  The default elasticsearch analyzer for annotation fields has been changed to
   "keyword" in order to provide more consistent case-sensitivity behaviours
   (#73, #88).
-  Made Flask an optional dependency: it is now possible to use the persistence
   components of the project without needing Flask (#76).
-  Python 3 compatibility (#72).


0.11.2 - 2014-07-25
-------------------

-  SECURITY: Fixed bug that allowed authenticated users to overwrite annotations
   on which they did not have permissions (#82).

0.11.1 - 2014-04-09
-------------------

-  Fixed support for using ElasticSearch instances behind HTTP Basic auth

0.11.0 - 2014-04-08
-------------------

-  Add support for ElasticSearch 1.0
-  Create changelog


