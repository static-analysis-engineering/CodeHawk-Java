## CodeHawk-Java browser-based user interface

The browser-based user interface is based on [flask](https://palletsprojects.com/p/flask/),
a lightweight [WSGI](https://wsgi.readthedocs.io/en/latest/) web application framework.

The easiest way to get started with flask is to use the python virtual environment:
```
> export PYTHONPATH=$HOME/CodeHawk-Java
> python -m venv venv
> source venv/bin/activate
(venv) > pip install flask
(venv) > export FLASK_APP=flask_app.py
(venv) > flask run
```
which will start a server listening on localhost:5000, which can be opened in
a browser.
