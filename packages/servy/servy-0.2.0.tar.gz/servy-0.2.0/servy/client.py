from __future__ import absolute_import

import urllib2
import urlparse

import servy.proto as proto
import servy.exc as exc


class Service(object):
    def __init__(self, name, host, scheme='http'):
        self.name = name

        self.host = host
        self.scheme = scheme

    @property
    def url(self):
        url = {
            'scheme': self.scheme,
            'netloc': self.host,
            'path': self.name,
            'params': '',
            'query': '',
            'fragment': '',
        }
        return urlparse.urlunparse(urlparse.ParseResult(**{k: v or '' for k, v in url.iteritems()}))

    def read(self, message):
        return urllib2.urlopen(self.url, message).read()


class Client(object):
    def __init__(self, service, proc=None):
        if isinstance(service, dict):
            service = Service(**service)
        self.__service = service
        self.__proc = proc

    def __getattr__(self, name):
        if self.__proc:
            proc = '{}.{}'.format(self.__proc, name)
        else:
            proc = name
        return Client(self.__service, proc)

    def __call__(self, *args, **kw):
        if not self.__proc:
            raise TypeError('\'proc\' argument must be a string, not \'NoneType\'')
        message = proto.Request.encode(self.__proc, args, kw)
        try:
            content = self.__service.read(message)
        except urllib2.HTTPError as e:
            if e.code == 404:
                raise exc.ServiceNotFound(self.__service.name)
            elif e.code == 501:
                raise exc.ProcedureNotFound(self.__proc)
            elif e.code == 503:
                message = e.read()
                try:
                    tb = proto.RemoteException.decode(message)
                except (ValueError, TypeError):
                    tb = ''
                raise exc.RemoteException(tb)
            else:
                raise

        return proto.Response.decode(content)
