# -*- coding: utf-8 -*-

import os
import time

import bunch
import colorclass
import requests
import six

from .compat import string_type
from .utils import formats, run_from_ipython


debug_messages = {
    'request': (
        '{blue}Executing {method} request:{/blue}\n'
        '{hiblack}'
        '    URL:     {url}\n'
        '    headers: {headers}\n'
        '    query:   {params}\n'
        '    data:    {data}\n'
        '{/hiblack}'
    ),
    'success_response': (
        '{green}Got {status_code} {reason}:{/green}\n'
        '{hiblack}'
        '    {text}\n'
        '{/hiblack}'
    ),
    'failure_response': (
        '{red}Got {status_code} {reason}:{/red}\n'
        '{hiblack}'
        '    {text}\n'
        '{/hiblack}'
    ),
    'cached_response': (
        '{cyan}Cached response:{/cyan}\n'
        '{hiblack}'
        '    {text}\n'
        '{/hiblack}'
    ),
    'nojson_response': (
        '{red}Got {status_code} {reason} (NOT JSON):{/red}\n'
        '{hiblack}'
        '    {text}\n'
        '{/hiblack}'
    )
}


DEBUG_MAX_TEXT_LENGTH = 100


if os.name == 'nt':
    if run_from_ipython():
        # IPython stops working properly when it loses control of
        # `stdout` on Windows. In this case we won't enable Windows
        # color support and we'll strip out all colors from the debug
        # messages.
        colorclass.disable_all_colors()
    else:
        colorclass.Windows.enable()


class Client(object):
    """Wrapper around the most basic methods of the requests library."""

    def __init__(self, debug=False):
        self.headers = bunch.Bunch()
        self.debug = debug
        self.cache = {}
        self.session = requests.session()

    def _log(self, message, debug=None, **kwargs):
        """Outputs a colored and formatted message in the console
        if the debug mode is activated.

        :param message: the message that will be printed
        :param debug: (optional) Overwrite of `Client.debug`
        :param kwargs: (optional) Arguments that will be passed
            to the `str.format()` method
        """
        display_log = self.debug
        if debug is not None:
            display_log = debug
        if display_log:
            colored_message = colorclass.Color(message)
            print((colored_message.format(**kwargs)))

    def request(self, method, url, path=(), extension=None, params=None,
                headers=None, data=None, debug=None, cache_lifetime=None,
                silent=False, ignore_cache=False, format='json', **kwargs):
        """Requests a URL and returns a *Bunched* response.

        This method basically wraps the request method of the requests
        module and adds a `path` and `debug` option.

        A `ValueError` will be thrown if the response is not JSON encoded.

        :param method: The request method, e.g. 'get', 'post', etc.
        :param url: The URL to request
        :param path: (optional) Appended to the request URL. This can be
            either a string or a list which will be joined
            by forward slashes.
        :param params: (optional) The URL query parameters
        :param headers: (optional) Extra headers to sent with the request.
            Existing header keys can be overwritten.
        :param data: (optional) Dictionary
        :param debug: (optional) Overwrite of `Client.debug`
        :param kwargs: (optional) Arguments that will be passed to
            the `requests.request` method
        :return: :class:`Bunch` object from JSON-parsed response
        """

        if not isinstance(path, string_type):
            path = '/'.join(path)

        request_headers = dict(self.headers.__dict__)
        if headers is not None:
            request_headers.update(headers)
        request_headers.setdefault('Content-Type',
                                   formats.meta(format).get('content_type'))

        if debug is None:
            debug = self.debug

        if extension is None:
            extension = ''
        elif not extension.startswith('.'):
            extension = '.' + extension

        url = url + path + extension

        self._log(debug_messages['request'], debug,
                  method=method.upper(), url=url, headers=request_headers,
                  params=params, data=data)

        cache_key = (url, str(params), str(headers))
        if cache_key in self.cache and not ignore_cache:
            item = self.cache[cache_key]
            if item['expires'] > time.time():
                self._log(debug_messages['cached_response'], debug,
                          text=item['value'])
                return bunch.bunchify(item['value'])
            del self.cache[cache_key]

        r = self.session.request(method, url, params=params,
                                 headers=request_headers, data=data, **kwargs)

        try:
            has_body = len(r.text) > 0
            if not has_body:
                parsed_response = 'No response'
            else:
                parsed_response = formats.parse(format, r.text)
        except ValueError as e:
            if len(r.text) > DEBUG_MAX_TEXT_LENGTH:
                text = r.text[:DEBUG_MAX_TEXT_LENGTH] + '...'
            else:
                text = r.text
            self._log(debug_messages['nojson_response'], debug,
                      status_code=r.status_code, reason=r.reason, text=text)
            if silent:
                return None
            raise e

        if cache_lifetime and cache_lifetime > 0 and method.lower() == 'get':
            self.cache[cache_key] = {'expires': time.time() + cache_lifetime,
                                     'value': parsed_response}

        debug_message = 'success_response' if r.status_code == 200 else \
            'failure_response'
        self._log(debug_messages[debug_message], debug,
                  status_code=r.status_code, reason=r.reason,
                  text=parsed_response)

        if has_body:
            return bunch.bunchify(parsed_response)
        return None


class Wrap(object):
    """Represents a part of the wrapped URL.

    You can chain this object to other Wrap objects. This is done
    *automagically* when accessing non-existing attributes of the object.

    The root of the chain should be a :class:`Client` object. When a new
    :class:`Wrap` object is created without a parent, it will create a
    new :class:`Client` object which will act as the root.
    """

    def __init__(self, part, parent=None, headers=None, params=None,
                 debug=None, cache_lifetime=None, silent=False,
                 extension=None):
        if isinstance(part, string_type):
            # trailing slashes are removed
            self._part = part[:-1] if part[-1:] == '/' else part
        else:
            self._part = str(part)
        self._url = None
        self._parent = parent or Client(debug=debug)
        self.config = bunch.Bunch(
            headers=bunch.bunchify(headers) if headers else bunch.Bunch(),
            params=bunch.bunchify(params) if params else bunch.Bunch(),
            debug=debug,
            cache_lifetime=cache_lifetime,
            silent=silent,
            extension=extension,
        )

    def url(self):
        if self._url:
            return self._url
        try:
            self._url = '/'.join([self._parent.url(), self._part])
        except AttributeError:
            self._url = self._part
        return self._url

    def __call__(self, *parts, **options):
        """Creates and returns a new :class:`Wrap` object in the chain
        if `part` is provided. If not, the current object's options
        will be manipulated by the provided `options` ``dict`` and the
        current object will be returned.

        Usage::

            # creates a new Wrap, assuming `foo` is already wrapped
            foo('bar')

            # this is the same as:
            foo.bar()

            # which is the same as:
            foo.bar

            # enabling `debug` for a specific chain object
            foo.bar(debug=True)

        :param part: (optional) The URL part to append to the current chain
        :param options: (optional) Arguments accepted by the
            :class:`Wrap` initializer
        """
        self.config.update(**options)

        if len(parts) == 0:
            return self

        parent = self
        for part in parts:
            # check if a wrap is already created for the part
            try:
                # the next part in this loop will have this wrap as
                # its parent
                parent = parent.__dict__[part]
            except KeyError:
                # create a wrap for the part
                parent.__dict__[part] = Wrap(part=part, parent=parent)
                parent = parent.__dict__[part]

        return parent

    def __getattr__(self, part):
        try:
            return self.__dict__[part]
        except KeyError:
            self.__dict__[part] = Wrap(part=part, parent=self,
                                       debug=self.config.get('debug'))
            return self.__dict__[part]

    def request(self, method, *parts, **options):
        """Requests a URL and returns a *Bunched* response.

        This method basically wraps the request method of the requests
        module and adds a `path` and `debug` option.

        :param method: The request method, e.g. 'get', 'post', etc.
        :param part: (optional) A primary key to append to the path
        :param url: (optional) The URL to request
        :param path: (optional) Appended to the request URL. This can be
            either a string or a list which will be joined
            by forward slashes.
        :param params: (optional) The URL query parameters
        :param headers: (optional) Extra headers to sent with the request.
            Existing header keys can be overwritten.
        :param data: (optional) Dictionary
        :param debug: (optional) Overwrite of `Client.debug`
        :param kwargs: (optional) Arguments that will be passed to
            the `requests.request` method
        :return: :class:`Bunch` object from JSON-parsed response
        """
        if len(parts) != 0:
            # the chain will be extended with the parts and finally a
            # request will be triggered
            return self.__call__(*parts).request(method=method, **options)

        else:
            if 'url' not in options:
                # the last part constructs the URL
                options['url'] = self.url()

            for key, value in six.iteritems(self.config):
                # set the defaults in the options
                if value is not None:
                    if isinstance(value, dict):
                        # prevents overwriting default values in dicts
                        copy = value.copy()
                        if options.get(key):
                            copy.update(options[key])
                        options[key] = copy
                    options.setdefault(key, value)

            # at this point, we're ready to completely go down the chain
            return self._parent.request(method=method, **options)

    def get(self, *parts, **options):
        """Executes a `GET` request on the currently formed URL."""
        return self.request('get', *parts, **options)

    def post(self, *parts, **options):
        """Executes a `POST` request on the currently formed URL."""
        return self.request('post', *parts, **options)

    def put(self, *parts, **options):
        """Executes a `PUT` request on the currently formed URL."""
        return self.request('put', *parts, **options)

    def patch(self, *parts, **options):
        """Executes a `PATCH` request on the currently formed URL."""
        return self.request('patch', *parts, **options)

    def delete(self, *parts, **options):
        """Executes a `DELETE` request on the currently formed URL."""
        return self.request('delete', *parts, **options)

    def head(self, *parts, **options):
        """Executes a `HEAD` request on the currently formed URL."""
        return self.request('head', *parts, **options)

    def __repr__(self):
        return "<{} for {}>".format(self.__class__.__name__, self.url())
