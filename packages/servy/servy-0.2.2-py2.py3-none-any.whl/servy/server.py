from __future__ import absolute_import

import inspect
import sys
import traceback

import webob.exc
import webob.dec
import webob.response

import servy.proto as proto


class Inspector(object):

    @staticmethod
    def is_procedure(obj):
        return (
            inspect.ismethod(obj) or
            inspect.isfunction(obj)
        )

    @staticmethod
    def is_container(obj):
        return (
            isinstance(obj, dict) or
            (inspect.isclass(obj) and issubclass(obj, Container)) or
            isinstance(obj, Container)
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
            procedures = {k: v for k, v in obj.items() if cls.is_procedure(v)}.items()
            containers = {k: v for k, v in obj.items() if cls.is_container(v)}.items()
        else:
            procedures = inspect.getmembers(obj, cls.is_procedure)
            containers = inspect.getmembers(obj, cls.is_container)

        procedures = cls.get_public(procedures)
        containers = cls.get_public(containers)
        return containers, procedures

    @classmethod
    def find(cls, container):
        containers_tree, procedures_tree = cls.analyze(container)
        while containers_tree:
            for namespace in containers_tree.copy():
                container = containers_tree.pop(namespace)
                if namespace.count('.') > 3:
                    continue
                containers, procedures = cls.analyze(container)
                for procedure in procedures:
                    procedures_tree['{}.{}'.format(namespace, procedure)] = \
                        procedures[procedure]
                for container in containers:
                    containers_tree['{}.{}'.format(namespace, container)] = \
                        containers[container]

        return procedures_tree


class Container(object):
    pass


class Server(object):
    def __init__(self, _container=None, **procedures):
        if _container:
            self.procedures = Inspector.find(_container)
        else:
            self.procedures = {}
            for name, proc in procedures.items():
                if not Inspector.is_procedure(proc):
                    continue
                self.procedures[name] = proc

    @webob.dec.wsgify
    def __call__(self, request):
        if request.method == 'POST':
            return self.rpc(request)
        elif request.method == 'GET':
            return self.docs()
        raise webob.exc.HTTPMethodNotAllowed

    def docs(self):
        docs = {}
        for name, proc in self.procedures.items():
            docs[name] = inspect.getdoc(proc)

        content = ''
        for fn, docstring in docs.items():
            content = '{}{}\n    {}\n\n'.format(content, fn, docstring)
        return content

    def rpc(self, request):
        procedure = request.path[1:]
        if procedure not in self.procedures:
            raise webob.exc.HTTPNotFound

        procedure = self.procedures[procedure]

        try:
            args, kw = proto.Request.decode(request.body)
        except:
            raise webob.exc.HTTPBadRequest

        try:
            content = procedure(*args, **kw)
        except:
            tb = ''.join(traceback.format_exception(*sys.exc_info()))
            message = proto.RemoteException.encode(tb)
            raise webob.exc.HTTPServiceUnavailable(body=message)

        return proto.Response.encode(content)
