"""Extensible Flask MIME encoders and decoders."""

__all__ = 'MimeEncoders'.split()
__version__ = '0.1.1'

from flask import request, Response

class MimeEncoders(object):
    def __getitem__(self, key):
        return isinstance(key, basestring) and getattr(self, key, None) or (self.default if key else self.null)

    def __iter__(self):
        return (k for k in dir(self) if not k.startswith('_'))

    def __str__(self):
        return '{}.{}({})'.format(self.__class__.__module__, self.__class__.__name__.lower(), ', '.join(self))

class MimeEncoder(object):
    name = 'base'
    mimetype = None
    encoders = MimeEncoders

    @classmethod
    def mimetyped(cls, mimetype=None, **response_options):
        if mimetype is None or callable(mimetype):
            view = mimetype
            mimetype = cls.mimetype
            if mimetype is None:
                return view if view else lambda f: f
        else:
            view = None

        def decorator(view):
            @wraps(view)
            def decorated_view(*args, **kwargs):
                response = view(*args, **kwargs)
                if isinstance(response, Response):
                    response.mimetype = mimetype
                    return response
                else:
                    return Response(response, mimetype = mimetype, **response_options)
            return decorated

        return decorator(view) if view else decorator

    @classmethod
    def autoencoded(cls, view):
        return view

    @classmethod
    def autodecoded(cls, view):
        return view

    @classmethod
    def make_response(cls, data, **options):
        return Response(str(data), **options)

    @classmethod
    def get_request_data(cls, request=request, **options):
        return dict(data=request.data) if request.data else {}

    @classmethod
    def loads(_cls, s, *args, **kwargs):
        return dict(data=s) if s else {}

    @classmethod
    def dumps(_cls, obj, *args, **kwargs):
        return str(obj)

MimeEncoders.base = MimeEncoder
MimeEncoders.null = None
