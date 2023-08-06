Flask-JSON
==========

.. image:: https://travis-ci.org/skozlovf/flask-json.png?branch=master
   :target: https://travis-ci.org/skozlovf/flask-json

Flask-JSON is a simple extension that adds better JSON support to Flask
application.

Features:

* Works on python 2.6, 2.7, 3.3+ and Flask 0.10+
* More ways to generate JSON responses (comparing to plain Flask)
* Extended JSON encoding support.

Usage
-----

Here is fast example::

    from datetime import datetime
    from flask import Flask
    from flask_json import FlaskJSON, JsonErrorResponse, json_response

    app = Flask(__name__)
    FlaskJSON(app)


    @app.route('/get_time')
    def get_time():
        return json_response(time=datetime.utcnow())


    @app.route('/raise_error')
    def raise_error():
        raise JsonErrorResponse(description='Example text.', code=123)


    if __name__ == '__main__':
        app.run()

Responses::

    GET /get_time HTTP/1.1

    HTTP/1.0 200 OK
    Content-Type: application/json
    Content-Length: 60

    {
      "status": 200,
      "time": "2015-04-14T13:17:16.732000"
    }

::

    GET /raise_error HTTP/1.1

    HTTP/1.0 400 BAD REQUEST
    Content-Type: application/json
    Content-Length: 70

    {
      "code": 123,
      "description": "Example text.",
      "status": 400
    }

Documentation
-------------

Documentation is available on `Read the Docs <http://flask-json.readthedocs.org>`_.
