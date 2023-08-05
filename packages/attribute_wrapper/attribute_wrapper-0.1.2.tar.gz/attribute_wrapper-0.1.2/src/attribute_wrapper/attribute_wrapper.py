#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
import json
import requests
from os.path import join


# Classes =====================================================================
class GenericWrapper(object):
    """
    Generic attribute-access object, which create URL paths from attribute
    calls.

    Each attribute access (``.path`` for example) is mapped to URL path
    (``URL/path`` for example).

    Each call of the attribute (``obj.path.get()``) is then translated to
    :method:`.download_handler` call as ``.download_handler("get", "URL/path",\
    **kwargs)``.

    You can subclass this class and redefine :method:`.download_handler` to
    server your own needs - see :class:`JSONWrapper` and :class:`HTTPWrapper`.

    Attributes:
        url (str): Part of the URL in linked list chain. See
                   :method:`.get_url` for details.
        parent (obj): Reference to parent in linked list chain.
        suffix (str): Optional suffix, which will be added to URL.
    """
    def __init__(self, url, parent=None, suffix=None):
        """
        Args:
            url (self): Base URL of the HTTP resource you want to access.
        """
        self.url = url
        self.parent = parent
        self.suffix = suffix

        # get specials from parent if defined
        self.specials = self._get_root().specials if self.parent else {
            "__dot__": ".",
            "__slash__": "/",
            "__dash__": "-",
        }

    def download_handler(self, method, url, data):
        """
        Here should be your definition of this method, which is expected to
        take some data and return result.

        Args:
            method (str): Last part of the attribute path before call -
                   ``obj.something.get()`` will render `get` as `method`.
            url (str): Hopefully valid URL composed from attribute paths.
            data (dict): Parameters given to attribute call.
        """
        raise NotImplementedError(
            "You should implement `.download_handler()` in your code!"
        )

    def __call__(self, **kwargs):
        """
        Handle calls to attribute.
        """
        url = self.get_url(True)
        url = self._replace_specials(url)

        # add suffix to non-domain urls
        if self.parent.parent and self.suffix:
            url += self.suffix

        # params = args if args else kwargs
        return self.download_handler(
            method=self.url,  # this is the last part of the attribute access
            url=url,
            data=kwargs if kwargs else None,
        )

    def _replace_specials(self, url):
        """
        In `url` replace keys from :attr:`specials` with correspondings vals.

        Args:
            url (str): String where the values are replaced.

        Returns:
            str: Updated string.
        """
        for key, val in self.specials.iteritems():
            url = url.replace(key, val)

        return url

    def _get_root(self):
        """
        Get root object from the hierarchy.

        Returns:
            obj: :class:`Recurser` instance of the root object.
        """
        if self.parent:
            return self.parent._get_root()

        return self

    def get_url(self, called=False):
        """
        Compose url from self and all previous items in linked list.

        Args:
            called (bool, default False): Switch to let the function knows,
                   that it should ignore the last part of the URL, which is
                   method type.

        Returns:
            str: Composed URL.
        """
        if not self.parent:
            return self.url

        # last call (called=True) is used for determining http method
        if called:
            return self.parent.get_url()
        else:
            return join(self.parent.get_url(), self.url)

    def __getattr__(self, attr):
        """
        Take care of URL composition.
        """
        return self.__dict__.get(
            attr,
            self.__class__(attr, self, self.suffix)
        )


class JSONWrapper(GenericWrapper):
    """
    Special example of :class:`GenericWrapper`, which translates all calls
    and given data to JSON and send it **as body** to given URL.

    Functions also adds ``content-type: application/json`` header to each
    request.
    """
    def download_handler(self, method, url, data):
        if data:
            data = json.dumps(data)

        headers = {
            'content-type': 'application/json'
        }

        resp = requests.request(method, url, headers=headers, data=data)

        # handle http errors
        resp.raise_for_status()

        return json.loads(resp.text)


class HTTPWrapper(GenericWrapper):
    """
    Example of :class:`GenericWrapper`, which translates all calls and given
    data to HTTP form parameters.
    """
    def download_handler(self, method, url, data):
        resp = requests.request(method, url, params=data)

        # handle http errors
        resp.raise_for_status()

        return resp.text
