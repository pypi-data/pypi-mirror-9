__version__ = '0.1.0'

import re

from flask import request


def add_headers_to_fontawesome_static_files(response):
    """
    Fix for font-awesome files: after Flask static send_file() does its
    thing, but before the response is sent, add an
    Access-Control-Allow-Origin: *
    HTTP header to the response (otherwise browsers complain).
    See:
    http://greenash.net.au/thoughts/2014/12/
    conditionally-adding-http-response-headers-in-flask-and-apache/
    """

    if (request.path and
        re.search(r'\.(ttf|woff|woff2|svg|eot)$', request.path)):
        response.headers.add('Access-Control-Allow-Origin', '*')

    return response


class FontAwesomeHeaders(object):
    """ Enables Flask Font-Awesome CORS HTTP response headers."""

    def __init__(self, app=None):
        self.app = app

        if self.app:
            self.init_app(self.app)

    def init_app(self, app):
        """ Configures Flask Font-Awesome Headers."""

        app.after_request(add_headers_to_fontawesome_static_files)
