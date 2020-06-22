from functools import wraps


def check_type(obj_type):
    def real_decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
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

            resp = client.get(ao_uri, params={'resolve': ['top_container::container_locations']})
            if resp.status_code != 200:
                raise Exception("Unable to fetch archival object with resolved container locations")

            if not isinstance(args[0], obj_type):
                raise TypeError("{} is not a {}".format(args[0], obj_type))
            return func(*args, **kwargs)
        return wrapper
    return real_decorator
