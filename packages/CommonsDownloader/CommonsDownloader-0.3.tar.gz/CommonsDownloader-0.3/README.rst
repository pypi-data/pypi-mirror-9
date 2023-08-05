CommonsDownloader
=================

|Build Status| |Coverage Status| |Code Health| |Documentation Status|
|Pypi| |License|

Tool to download thumbnails of files from Wikimedia Commons

Usage
-----

This tool can be used either by passing the filenames or by using a file
list.

Using filenames
~~~~~~~~~~~~~~~

Just list the files we want to download.

::

    download_from_Wikimedia_Commons.py Example.jpg Example_ka.png

You can set the width of the thumbnail by using the ``--width``
argument:

::

    download_from_Wikimedia_Commons.py --width 50 Example.jpg Example_ka.png

Using a file list
~~~~~~~~~~~~~~~~~

The file list must be formated as following, with one file per line, and
``filename,width``:

::

    Example.jpg,100
    Example ka.png,80

Then use the ``--list`` argument:

::

    download_from_Wikimedia_Commons.py --list list.txt

Setting the output folder
~~~~~~~~~~~~~~~~~~~~~~~~~

By default, the tool downloads the files in the current directory.

This can be changed using the ``--output`` flag with a valid path.

::

    download_from_Wikimedia_Commons.py Example.jpg --output some/path/

Verbosity
~~~~~~~~~

By default, the tool display basic information its logs (through
``logging``).

You can adjust the verbosity level with the ``-v`` and ``-q`` flags: use
``-v`` to display DEBUG-level messages, ``-q`` to silence INFO-level
messages.

Installation
------------

Easiest way to install is to use ``pip``:

::

    pip install git+git://github.com/Commonists/CommonsDownloader.git#egg=CommonsDownloader

Alternatively, you can clone the repository and install it using
``setuptools``:

::

    python setup.py install

This will install the executable script
``download_from_Wikimedia_Commons.py``

.. |Build Status| image:: https://travis-ci.org/Commonists/CommonsDownloader.svg?branch=master
   :target: https://travis-ci.org/Commonists/CommonsDownloader
.. |Coverage Status| image:: https://coveralls.io/repos/Commonists/CommonsDownloader/badge.svg?branch=master
   :target: https://coveralls.io/r/Commonists/CommonsDownloader?branch=master
.. |Code Health| image:: https://landscape.io/github/Commonists/CommonsDownloader/master/landscape.svg?style=flat
   :target: https://landscape.io/github/Commonists/CommonsDownloader/master
.. |Documentation Status| image:: https://readthedocs.org/projects/commonsdownloader/badge/?version=latest
   :target: https://readthedocs.org/projects/commonsdownloader/?badge=latest
.. |Pypi| image:: https://img.shields.io/pypi/v/CommonsDownloader.svg?style=flat
   :target: https://pypi.python.org/pypi/CommonsDownloader
.. |License| image:: https://img.shields.io/pypi/l/CommonsDownloader.svg?style=flat
   :target: http://opensource.org/licenses/MIT
