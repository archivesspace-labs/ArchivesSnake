import json
from functools import wraps


def jsonify():
    def real_decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            updated = list(args)
            if callable(getattr(args[0], 'json', None)):
                updated[0] = args[0].json()
            elif isinstance(args[0], str):
                updated[0] = args[0].loads(args[0])
            return func(*updated, **kwargs)
        return wrapper
    return real_decorator
