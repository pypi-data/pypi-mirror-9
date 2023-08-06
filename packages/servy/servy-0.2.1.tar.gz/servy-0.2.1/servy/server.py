from __future__ import absolute_import

import inspect
import sys
import traceback

import webob.exc
import webob.dec
import webob.response

import servy.proto as proto


class ServiceInspector(object):

    @staticmethod
    def is_service(obj):
        return (
            inspect.ismethod(obj) or
            inspect.isfunction(obj) or
            (isinstance(obj, Service) and callable(obj))
        )

    @staticmethod
    def is_container(obj):
        return (
            isinstance(obj, dict) or
            (inspect.isclass(obj) and issubclass(obj, Service)) or
            isinstance(obj, Service)
        )

    @staticmethod
    def get_public(items):
        return {k: v for k, v in items if (
            not (k.startswith('_') or k.startswith('__')) and
            k not in ('im_class', 'im_self', 'im_func')
        )}

    @classmethod
    def analyze(cls, obj):
        if isinstance(obj, dict):
            services = {k: v for k, v in obj.items() if cls.is_service(v)}.items()
            containers = {k: v for k, v in obj.items() if cls.is_container(v)}.items()
        else:
            services = inspect.getmembers(obj, cls.is_service)
            containers = inspect.getmembers(obj, cls.is_container)

        services = cls.get_public(services)
        containers = cls.get_public(containers)
        return containers, services

    @classmethod
    def find(cls, container):
        containers_tree, services_tree = cls.analyze(container)
        while containers_tree:
            for namespace in containers_tree.copy():
                container = containers_tree.pop(namespace)
                if namespace.count('.') > 3:
                    continue
                containers, services = cls.analyze(container)
                for service in services:
                    services_tree['{}.{}'.format(namespace, service)] = \
                        services[service]
                for container in containers:
                    containers_tree['{}.{}'.format(namespace, container)] = \
                        containers[container]

        return services_tree


class Service(object):
    pass


class Server(object):
    def __init__(self, _server=None, **services):
        if _server:
            self.services = ServiceInspector.find(_server)
        else:
            self.services = {}
        self.services.update(services)

    @webob.dec.wsgify
    def __call__(self, request):
        if request.method == 'POST':
            return self.rpc(request)
        raise webob.exc.HTTPMethodNotAllowed

    def rpc(self, request):
        service = request.path[1:]
        if service not in self.services:
            raise webob.exc.HTTPNotFound

        service = self.services[service]

        try:
            args, kw = proto.Request.decode(request.body)
        except:
            raise webob.exc.HTTPBadRequest

        try:
            content = service(*args, **kw)
        except:
            tb = ''.join(traceback.format_exception(*sys.exc_info()))
            message = proto.RemoteException.encode(tb)
            raise webob.exc.HTTPServiceUnavailable(body=message)

        content = proto.Response.encode(content)
        return webob.response.Response(content)
