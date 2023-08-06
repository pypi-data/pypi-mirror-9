
import sys
import json

from django.utils import six

from django.db import DEFAULT_DB_ALIAS

from django.core.serializers.base import DeserializationError
from django.core.serializers import get_serializer_formats, register_serializer
from django.core.serializers.json import (
  Serializer as JsonSerializer,
  PythonDeserializer,
)

from .migrator import migrate_to, MigrationsNeeded

json_header = {}

class Serializer(JsonSerializer):
    """This will attempt to be backwards compatible"""
    def start_serialization(self):
        super(Serializer, self).start_serialization()
        if json_header:
            json_header['fields'] = {}
            json_header['model'] = "auth.user"
            json.dump(json_header, self.stream, **self.json_kwargs)
            self.stream.write(',')


def Deserializer(stream_or_string, **options):
    """
    We are replacing the json deserializer completly.
    """
    if not isinstance(stream_or_string, (bytes, six.string_types)):
        stream_or_string = stream_or_string.read()
    if isinstance(stream_or_string, bytes):
        stream_or_string = stream_or_string.decode('utf-8')
    try:
        objects = json.loads(stream_or_string)
        for obj in objects:
            if 'migrations' in obj:
                db = options.get('using', DEFAULT_DB_ALIAS)
                migrate_to(obj['migrations'], db)
            break
        for obj in PythonDeserializer(objects, **options):
            yield obj
    except GeneratorExit:
        raise
    except MigrationsNeeded as error:
        print(error)
    except Exception as e:
        # Map to deserializer error
        six.reraise(DeserializationError, DeserializationError(e), sys.exc_info()[2])


def json_serializer(data, name='migrated_json'):
    """Register our own serializer with it's own ken"""
    get_serializer_formats()
    from django.core.serializers import _serializers
    global _serializers
    global json_header
    register_serializer(name, 'fast_fixtures.serializers', _serializers)
    json_header = data
    return name

def json_deserializer():
    return json_serializer(data=None, name='json')

