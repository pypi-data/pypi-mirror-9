from __future__ import absolute_import

import urllib2
import urlparse

import servy.proto as proto
import servy.exc as exc


class Service(object):
    def __init__(self, host, name):
        self.host = host
        self.name = name

    @property
    def url(self):
        url = {
            'scheme': 'http',
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
    def __init__(self, host, service=None):
        self.host = host
        if service:
            service = Service(host, service)
        self.__service = service

    def __getattr__(self, name):
        if self.__service:
            service = '{}.{}'.format(self.__service.name, name)
        else:
            service = name
        return Client(self.host, service)

    def __call__(self, *args, **kw):
        if not self.__service:
            raise TypeError('\'service\' argument must be a string, not \'NoneType\'')
        message = proto.Request.encode(args, kw)
        try:
            content = self.__service.read(message)
        except urllib2.HTTPError as e:
            if e.code == 404:
                raise exc.ServiceNotFound(self.__service.name)
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
