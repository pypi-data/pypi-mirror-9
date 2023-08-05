AttributeWrapper
================

.. image:: https://badge.fury.io/py/attribute_wrapper.png
    :target: http://badge.fury.io/py/attribute_wrapper

.. image:: https://pypip.in/d/attribute_wrapper/badge.png
        :target: https://crate.io/packages/attribute_wrapper?version=latest

This wrapper maps attribute calls to HTTP API. The package provides similar
functionality as `Tortilla <https://github.com/redodo/tortilla>`_, but it is
implemented in smaller and simpler code.

This simplicity gives you ability to subclass and modify functionality as you
need.

Examples
--------
Basic access
++++++++++++

.. code-block:: python

    from attribute_wrapper import HTTPWrapper

    r = HTTPWrapper("http://kitakitsune.org")
    data = r.get()

This will download content of http://kitakitsune.org and return it as string. The ``.get()`` call determines the HTTP method, which is used to perform the request.

Attribute path composition
++++++++++++++++++++++++++
The dot attribute access notation is used to compose the path of required HTTP resource. For example::

    r.raw.get()

is translated to GET request for http://kitakitsune.org/raw.

Special characters
++++++++++++++++++
The dot notation in python is restricted only to A-Z, a-z, 0-9 and _, which may be sometimes too much restricting. Thats why the ``GenericWrapper`` has the attribute ``.specials``, which contains mappings of special sequences to URL characters.

The ``.specials`` table is at this moment implemented by following structure:

.. code-block:: python

    {
        "__dot__": ".",
        "__slash__": "/",
        "__dash__": "-",
    }

Which means that URL containing this substrings will be translated as expected:

.. code-block:: python

    r.raw.doctene_knihy__dot__txt.get()

is translated to http://kitakitsune.org/raw/doctene_knihy.txt

This functionality can be changed by replacing ``.specials`` dictionary table with something else, or with blank dictionary to disable it.

Automatic suffix
++++++++++++++++
If you work with API, which expects that each file ends with suffix like ``.json`` or ``.html``, you can modify the ``.suffix`` attribute or add ``suffix`` parameter when you are instancing the class:

.. code-block:: python

    r = HTTPWrapper("http://kitakitsune.org", suffix=".txt")

    # this will return content of the http://kitakitsune.org, because the suffix
    # is ignored in root of the path
    r.get()

    # this will return http://kitakitsune.org/raw/doctene_knihy.txt
    r.raw.doctene_knihy.get()

Parameters
++++++++++
The method handling call at last attribute accepts keyword parameters, which are sent to server as form data:

.. code-block:: python

    r.post(something="else")

This will send ``{"something": "else"}`` dictionary as POST data to server.

JSONWrapper
+++++++++++
As example subclass, there is also ``JSONWrapper``, which translates all parameters to JSON and send it as HTTP **body** to server. This may be specially useful with some of the REST API.

Subclassing
-----------
The code is actually really simple (170 lines!) and it should be (at least I think) easy to understand. If you need some new functionality, you can just simply subclass the ``GenericWrapper`` class and rewrite the ``.download_handler()`` method to reflect your needs.

For example - the ``JSONWrapper`` is implemented in few lines of code:

.. code-block:: python

    import json

    class JSONWrapper(GenericWrapper):
        def download_handler(self, method, url, data):
            if data:
                data = json.dumps(data)

            headers = {
                'content-type': 'application/json'
            }

            resp = requests.request(method, url, headers=headers, data=data)

            return json.loads(resp.text)

Your code
+++++++++
Feel free to send pull request with you own classes (don't forget to document it). I would like to make this package useful and I will gladly incorporate your code, so you don't need to create your own package.

Installation
------------
The code is hosted at `PYPI <https://pypi.python.org/pypi/attribute_wrapper>`_,
and you can easily install it using the following command:

.. code-block:: bash

    sudo pip install attribute_wrapper
