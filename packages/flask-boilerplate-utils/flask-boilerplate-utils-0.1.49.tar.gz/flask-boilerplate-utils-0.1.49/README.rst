Flask Boilerplate Utilities
================================================

For use in `Flask-Boilerplate <https://github.com/nickw444/Flask-Boilerplate>`_.  however very useful as a standalone package for use within Flask apps.

This module is part of the flask-boilerplate project.

- `flask-boilerplate <https://github.com/nickw444/Flask-Boilerplate>`_
- `flask-boilerplate-buildutils <https://github.com/nickw444/flask-boilerplate-buildutils>`_
- `flask-boilerplate-utils <https://github.com/nickw444/flask-boilerplate-utils>`_
- `maketools <https://github.com/nickw444/python-maketools>`_

Installation
------------------------------------

.. code-block:: bash

	pip install flask-boilerplate-utils

Usage
-----------------------------------

.. code-block:: python

    from flask import Flask
    from flask_boilerplate_utils import Boilerplate()
    
    app = Flask(__name__)
    Boilerplate(app)


Full usage available at `read the docs <http://flask-boilerplate-utils.readthedocs.org/en/latest/>`_
