

import logging
log = logging.getLogger(__name__)

from .request import Request

class App(object):
    '''
    Base Application class.

    Create an instance of this, passing configuration options, and use the resulting instance as your WSGI application callable.

        application = App(root_view=myview)

    You can also sub-class this to provide the root_view.
    '''
    def __init__(self, **opts):
        for key, val in opts.items():
            setattr(self, key, val)

    def __call__(self, environ, start_response):
        request = Request(self, environ)

        response = self.root_view(request)

        start_response(response.status, response.build_headers())

        return response
