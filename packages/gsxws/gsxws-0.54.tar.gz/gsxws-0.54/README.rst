********
py-gsxws
********

gsxws is a Python library designed to work with Apple's GSX Web Services API.
The goal is for it to support all the features of the API. Currently it supports most of them.

Please consult the `GSXWS API documentation <https://gsxwsut.apple.com/apidocs/ut/html/WSHome.html>`_ for more details.


************
Requirements
************

- Python 2.7 or later
- lxml
- PyYAML
- A valid Apple ID with access to GSX Web Services.

Installation::

    pip install gsxws

... or grab the latest dev version::

	pip install -U -e git+git://github.com/filipp/py-gsxws.git#egg=gsxws


*****
Usage
*****

It goes a little something like this::
    
    # check warranty status
    import gsxws
    gsxws.connect(apple_id, password, sold_to)
    mac = gsxws.Product('70033CDFA4S')
    mac.warranty()

    # get available parts for this machine
    mac.parts()


Check the tests-folder for more examples.
