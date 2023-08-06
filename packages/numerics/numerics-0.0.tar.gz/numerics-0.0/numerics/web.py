#!/usr/bin/env python

"""
web handler for kplot
"""

from webob import Request, Response, exc

class Handler(object):

    def __init__(self, **kw):
        pass

    def __call__(self, environ, start_response):
        request = Request(environ)
        response = Response(content_type='text/plain',
                            body="kplot")
        return response(environ, start_response)

if __name__ == '__main__':
    from wsgiref import simple_server
    app = Handler()
    server = simple_server.make_server(host='0.0.0.0', port=8080, app=app)
    server.serve_forever()
          

