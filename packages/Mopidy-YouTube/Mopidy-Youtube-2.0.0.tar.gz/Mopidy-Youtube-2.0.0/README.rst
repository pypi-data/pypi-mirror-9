**************
Mopidy-Youtube
**************

.. image:: https://app.wercker.com/status/08a31153413287cd9a6965d8b7f26586/m
    :target: https://app.wercker.com/project/bykey/08a31153413287cd9a6965d8b7f26586
    :alt: CI build status

.. image:: https://img.shields.io/pypi/v/Mopidy-Youtube.svg?style=flat
    :target: https://pypi.python.org/pypi/Mopidy-Youtube/
    :alt: Latest PyPI version

.. image:: https://img.shields.io/pypi/dm/Mopidy-Youtube.svg?style=flat
    :target: https://pypi.python.org/pypi/Mopidy-Youtube/
    :alt: Number of PyPI downloads

.. image:: https://img.shields.io/coveralls/dz0ny/mopidy-youtube/master.svg?style=flat
   :target: https://coveralls.io/r/dz0ny/mopidy-youtube?branch=master
   :alt: Test coverage


Mopidy extension that plays sound from Youtube.


Installation
============

Make sure you already have the GStreamer plugins, if not you can install it by
running::

    $ sudo apt-get install gstreamer0.10-plugins-bad


Install by running::

    $ pip install Mopidy-Youtube


How to use
==========

Simply use search for filename in your MPD client or add Youtube url to
playlist prefixed by ``yt:``.

Example: ``yt:http://www.youtube.com/watch?v=Njpw2PVb1c0``

Example for playlist:
``yt:http://www.youtube.com/playlist?list=PLeCg_YDclAETQHa8VyFUHKC_Ly0HUWUnq``


If resolving stops working
==========================

Update pafy library::

   pip install pafy -U


Project resources
=================

- `Source code <https://github.com/dz0ny/mopidy-youtube>`_
- `Issue tracker <https://github.com/dz0ny/mopidy-youtube/issues>`_
- `Download development snapshot <https://github.com/dz0ny/mopidy-youtube/archive/master.tar.gz#egg=Mopidy-Youtube-dev>`_


Changelog
=========

v2.0.0 (2015-04-01)
-------------------

- Require Mopidy >= 1.0.

- Update to work with the new playback API in Mopidy 1.0.

- Update to work with the new search API in Mopidy 1.0.

v1.0.2 (2015-01-02)
-------------------

- Changelog missing.

v1.0.1 (2014-05-28)
-------------------

- Changelog missing.

v0.1.0 (2014-03-06)
-------------------

- Initial release.
