Decorator for flup's gzip compression WSGI middleware
=====================================================

Usage example::

    from wsgigzip import gzip

    @gzip()
    def index(environ, start_response):
        start_response('200 OK', [('Content-type', 'text/plain')])
        return ['Home Page']

    if __name__ == '__main__':
        from wsgiref.simple_server import make_server
        http = make_server('', 8080, index)
        http.serve_forever()
