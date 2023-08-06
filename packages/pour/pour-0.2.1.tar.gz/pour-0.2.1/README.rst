pour: flask boilerplate
=========================

.. image:: https://img.shields.io/pypi/v/pour.svg
    :target: https://pypi.python.org/pypi/pour

.. image:: https://img.shields.io/pypi/dm/pour.svg
        :target: https://pypi.python.org/pypi/pour


An ultra-lightweight command line tool to quickly generate a bare Flask app 
file for prototyping.

Installation
------------

To install pour, simply:

.. code-block:: bash

    $ pip install pour

Usage
-----

::

    $ pour --help
    usage: pour [-n NAME] [-t]

    A lightweight Flask app generator.
    --------------------------------------------------------------------------
    https://github.com/keyanp/pour

    optional arguments:
      --help         Show this help message and exit
      -n NAME        Set a name for the generated app (default is app)
      -t             Include test file


For example, typing:

.. code-block:: bash

    $ pour 

Saves a file named ``app.py`` to the current working directory:

.. code-block:: python
    
    from flask import Flask
    app = Flask(__name__)


    @app.route('/')
    def index():
        return 'Hello World!'

    if __name__ == '__main__':
        app.run(Debug=True)
