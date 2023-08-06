"""Flask MIME JSON encoder and decoder."""

__all__ = 'JsonMimeEncoder'.split()

from . import MimeEncoders
from flask import json, request, Response
from functools import wraps

class JsonMimeEncoder(MimeEncoders.base):
    """Flask MIME JSON encoder and decoder."""
    name = 'json'
    mimetype = 'application/json'

    JSONEncoder = json.JSONEncoder
    JSONDecoder = json.JSONDecoder

    @classmethod
    def autoencoded(cls, view):
        @wraps(view)
        def decorated_view(**uri_params):
            response = view(**uri_params)

            if not isinstance(response, (Response, basestring)):
                response = cls.make_response(response)

            return response
        return decorated

    @classmethod
    def autodecoded(cls, view):
        @wraps(view)
        def decorated_view(**uri_params):
            uri_params.update(self.get_request_data())
            return view(**uri_params)
        return decorated

    @classmethod
    def make_response(cls, data, **options):
        options['mimetype'] = cls.mimetype
        return Response(cls.dumps(data), **options)

    @classmethod
    def get_request_data(cls, request=request, **options):
        if request.json:
            return request.json
        elif request.data:
            return self.loads(request.data, **options)
        else:
            return {}

    @classmethod
    def loads(_cls, s, **kwargs):
        if 'cls' not in kwargs:
            kwargs['cls'] = _cls.JSONDecoder
        return json.loads(s, **kwargs)

    @classmethod
    def dumps(_cls, obj, **kwargs):
        if 'cls' not in kwargs:
            kwargs['cls'] = _cls.JSONEncoder
        return json.dumps(obj, **kwargs)

MimeEncoders.json = JsonMimeEncoder
