import json
from collections.abc import Mapping
from functools import wraps


def jsonify():
    def real_decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # clone args to a list so it is mutable
            updated = list(args)

            ao_thingit = args[0]

            # if object has .json(), return that value
            if callable(getattr(ao_thingit, 'json', None)):
                updated[0] = ao_thingit.json()

            # if object is a string, convert to json
            elif isinstance(args[0], str):
                updated[0] = json.loads(ao_thingit)

            return func(*updated, **kwargs)
        return wrapper
    return real_decorator


def urify():
    def real_decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # clone args to a list so it is mutable
            updated = list(args)

            ao_thingit = args[0]
            ao_uri = None

            # if object has .json(), replace with value of .json()
            if callable(getattr(ao_thingit, 'json', None)):
                ao_thingit = ao_thingit.json()

            if isinstance(ao_thingit, str):
                ao_uri = ao_thingit
            elif isinstance(ao_thingit, Mapping):
                ao_uri = ao_thingit.get("uri", ao_thingit.get("ref", None))

            if not ao_uri:
                raise Exception('Object passed could not be understood as an Archival Object or URI')

            return func(*updated, **kwargs)
        return wrapper
    return real_decorator
