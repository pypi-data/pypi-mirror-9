SMART FHIR Client
=================

This is _fhirclient_, a flexible Python client for [FHIR][] servers supporting the [SMART on FHIR][smart] protocol.
The client is compatible with Python 2.7, possibly earlier, and Python 3.


Installation
------------

    pip install fhirclient


Documentation
-------------

Technical documentation is available at [docs.smarthealthit.org/client-py/][docs].

#### Flask App

Take a look at [`flask_app.py`][flask_app] to see how you can use the client in a simple (Flask) app.
This app starts a webserver, listening on [_localhost:8000_](http://localhost:8000), and prompts you to login to our sandbox server and select a patient.
It then goes on to retrieve the selected patient's demographics and med prescriptions and lists them in a simple HTML page.


Building Distribution
---------------------

    pip install -r requirements.txt
    python setup.py sdist
    python setup.py bdist_wheel


### Incrementing the lib version

    bumpversion patch
    bumpversion minor
    bumpversion major


Docs Generation
---------------

Docs are generated with [Doxygen][] and [doxypypy][].
You will need to install doxypypy the old-fashioned way, checking out the repo and issuing `python setup.py install`.
Then you can just run Doxygen, configuration is stored in the `Doxyfile`.

Running Doxygen will put the generated documentation into `docs`, the HTML files into `docs/html`.
Those files make up the content of the `gh-pages` branch.
I usually perform a second checkout of the _gh-pages_ branch and copy the html files over, with:

    doxygen
    rsync -a docs/html/ ../client-py-web/


[fhir]: http://www.hl7.org/implement/standards/fhir/
[smart]: http://docs.smarthealthit.org
[docs]: https://smart-on-fhir.github.io/client-py
[flask_app]: https://github.com/smart-on-fhir/client-py/blob/master/flask_app.py
[doxygen]: http://www.stack.nl/~dimitri/doxygen
[doxypypy]: https://github.com/Feneric/doxypypy
