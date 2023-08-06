"""Flask MIME JSON encoder and decoder supporting ISO8601 date/time format."""

__all__ = 'JsonIso8601MimeEncoder'.split()

from . import MimeEncoders, json
from datetime import date, time

class JsonIso8601MimeEncoder(MimeEncoders.json):
    """Flask MIME JSON encoder and decoder supporting ISO8601 date/time format."""

    class JSONEncoder(MimeEncoders.json.JSONEncoder):
        """JSON encoder supporting ISO8601 date/time format."""
        def default(self, value):
            if isinstance(value, (date, time)):
                return value.isoformat()
            return super(JSONEncoder, self).default(self, value)

MimeEncoders.json_iso8601 = JsonIso8601MimeEncoder
