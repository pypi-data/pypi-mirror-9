import json


class Message(object):
    pass


class Response(Message):
    name = 'response'

    @classmethod
    def encode(cls, content):
        message = {
            'message': cls.name,
            'content': content,
        }
        return json.dumps(message)

    @classmethod
    def decode(cls, content):
        message = json.loads(content)
        return message['content']


class Request(Message):
    name = 'request'

    @classmethod
    def encode(cls, proc, args, kw):
        message = {
            'message': cls.name,
            'content': {
                'proc': proc,
                'args': args,
                'kw': kw,
            },
        }
        return json.dumps(message)

    @classmethod
    def decode(cls, content):
        message = json.loads(content)
        return (
            message['content']['proc'],
            message['content']['args'],
            message['content']['kw'],
        )


class RemoteException(Message):
    name = 'exception'

    @classmethod
    def encode(cls, tb):
        message = {
            'message': cls.name,
            'content': tb,
        }
        return json.dumps(message)

    @classmethod
    def decode(cls, content):
        message = json.loads(content)
        return message['content']
