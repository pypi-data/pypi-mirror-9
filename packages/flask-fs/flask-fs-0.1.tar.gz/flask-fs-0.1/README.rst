========
Flask-FS
========

.. image:: https://secure.travis-ci.org/noirbizarre/flask-fs.png
    :target: http://travis-ci.org/noirbizarre/flask-fs
    :alt: Build status
.. image:: https://coveralls.io/repos/noirbizarre/flask-fs/badge.png?branch=master
    :target: https://coveralls.io/r/noirbizarre/flask-fs?branch=master
    :alt: Code coverage
.. image:: https://requires.io/github/noirbizarre/flask-fs/requirements.png?branch=master
    :target: https://requires.io/github/noirbizarre/flask-fs/requirements/?branch=master
    :alt: Requirements Status
.. image:: https://readthedocs.org/projects/flask-fs/badge/?version=latest
    :target: http://flask-fs.readthedocs.org/en/latest/
    :alt: Documentation status

Simple and easy file storages for Flask


Compatibility
=============

Flask-FS requires Python 2.7+ and Flask 0.10+.


.. Amazon S3 support requires Boto.

.. OpenStack Swift support requires python-swift-client.

.. GridFS support requires PyMongo.


Installation
============

You can install Flask-FS with pip:

.. code-block:: console

    $ pip install flask-fs

..    # or
..    $ pip install flask-fs[s3]  # For Amazon S3 backend support
..    $ pip install flask-fs[swift]  # For OpenStack swift backend support
..    $ pip install flask-fs[gridfs]  # For GridFS backend support
..    $ pip install flask-fs[all]  # To include all dependencies for all backends

or with easy_install:

.. code-block:: console

    $ easy_install flask-fs

..    # or
..    $ easy_install flask-fs[s3]  # For Amazon S3 backend support
..    $ easy_install flask-fs[swift]  # For OpenStack swift backend support
..    $ easy_install flask-fs[gridfs]  # For GridFS backend support
..    $ easy_install flask-fs[all]  # To include all dependencies for all backends


Quick start
===========

TODO: a quick hello world with Flask-Buckets

.. code-block:: python

    from flask import Flask
    from flask.ext import fs

    app = Flask(__name__)
    fs.init_app(app)

    images = fs.Storage('images')


    if __name__ == '__main__':
        app.run(debug=True)


Documentation
=============

The full documentation is hosted `on Read the Docs <http://flask-fs.readthedocs.org/en/latest/>`_
