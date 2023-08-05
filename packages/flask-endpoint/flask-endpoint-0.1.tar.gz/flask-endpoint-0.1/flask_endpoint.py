# -*- coding: utf-8 -*-

from flask import Blueprint
from werkzeug import import_string, cached_property


class LazyEndpoint(object):

    def __init__(self, import_name):
        self.__module__, self.__name__ = import_name.rsplit('.', 1)
        self.import_name = import_name

    @cached_property
    def endpoint(self):
        return import_string(self.import_name)


class Endpoint(Blueprint):

    def __init__(self, name, namespace, import_name, **kwargs):
        kwargs['url_prefix'] = namespace
        super(Endpoint, self).__init__(name, import_name, **kwargs)

    def _endpoint_route(self, f, method, path=None, **options):
        if not path:
            path = ''
        return self.add_url_rule(path, view_func=f, methods=[method], **options)

    def get(self, path=None, **options):
        def decorator(f):
            return self._endpoint_route(f, 'GET', path, **options)
        return decorator

    def post(self, path=None, **options):
        def decorator(f):
            return self._endpoint_route(f, 'POST', path, **options)
        return decorator

    def put(self, path=None, **options):
        def decorator(f):
            return self._endpoint_route(f, 'PUT', path, **options)
        return decorator

    def patch(self, path=None, **options):
        def decorator(f):
            return self._endpoint_route(f, 'PATCH', path, **options)
        return decorator

    def delete(self, path=None, **options):
        def decorator(f):
            return self._endpoint_route(f, 'DELETE', path, **options)
        return decorator

    def options(self, path=None, **options):
        def decorator(f):
            return self._endpoint_route(f, 'OPTIONS', path, **options)
        return decorator
