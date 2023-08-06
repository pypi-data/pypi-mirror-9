************
Mopidy-Beets
************

.. image:: https://img.shields.io/pypi/v/Mopidy-Beets.svg?style=flat
    :target: https://pypi.python.org/pypi/Mopidy-Beets/
    :alt: Latest PyPI version

.. image:: https://img.shields.io/pypi/dm/Mopidy-Beets.svg?style=flat
    :target: https://pypi.python.org/pypi/Mopidy-Beets/
    :alt: Number of PyPI downloads

.. image:: https://img.shields.io/travis/mopidy/mopidy-beets/master.svg?style=flat
    :target: https://travis-ci.org/mopidy/mopidy-beets
    :alt: Travis CI build status

.. image:: https://img.shields.io/coveralls/mopidy/mopidy-beets/master.svg?style=flat
   :target: https://coveralls.io/r/mopidy/mopidy-beets?branch=master
   :alt: Test coverage

`Mopidy <http://www.mopidy.com/>`_ extension for playing music from
`Beets <http://beets.radbox.org/>`_ via Beets' web extension.


Installation
============

Install by running::

    pip install Mopidy-Beets

Or, if available, install the Debian/Ubuntu package from `apt.mopidy.com
<http://apt.mopidy.com/>`_.


Configuration
=============

#. Setup the `Beets web plugin
   <http://beets.readthedocs.org/en/latest/plugins/web.html>`_.

#. Tell Mopidy where to find the Beets web interface by adding the following to
   your ``mopidy.conf``::

    [beets]
    hostname = 127.0.0.1
    port = 8888

#. Restart Mopidy.

#. Searches in Mopidy will now return results from your Beets library.


Usage
=====

#. Run ``beet web`` to start the Beets web interface.

#. Start Mopidy, and search or browse your Beets library with any Mopidy client.


Project resources
=================

- `Source code <https://github.com/mopidy/mopidy-beets>`_
- `Issue tracker <https://github.com/mopidy/mopidy-beets/issues>`_
- `Download development snapshot
  <https://github.com/mopidy/mopidy-beets/tarball/master#egg=Mopidy-Beets-dev>`_


Changelog
=========

v2.0.0 (2015-03-25)
-------------------

- Require Mopidy >= 1.0.

- Update to work with new playback API in Mopidy 1.0.

- Update to work with new backend search API in Mopidy 1.0.

v1.1.0 (2014-01-20)
-------------------

- Require Requests >= 2.0.

- Updated extension and backend APIs to match Mopidy 0.18.

v1.0.4 (2013-12-15)
-------------------

- Require Requests >= 1.0, as 0.x does not seem to be enough. (Fixes: #7)

- Remove hacks for Python 2.6 compatibility.

- Change search field ``track`` to ``track_name`` for compatibility with
  Mopidy 0.17. (Fixes: mopidy/mopidy#610)

v1.0.3 (2013-11-02)
-------------------

- Properly encode search queries containing non-ASCII chars.

- Rename logger to ``mopidy_beets``.

v1.0.2 (2013-04-30)
-------------------

- Fix search.

v1.0.1 (2013-04-28)
-------------------

- Initial release.
