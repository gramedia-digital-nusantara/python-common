import json
import os

from jsonschema import RefResolver, validators


class CorJsonResolver(RefResolver):
    """ Allows JSON schema to resolve references to other JSONSchemas within our project directory
    """
    def resolve_remote(self, uri):
        _this_dir = os.path.abspath(os.path.dirname(__file__), )
        _app_base_dir = os.path.join(_this_dir, os.pardir)

        try:
            uri = uri.replace(self.base_uri, '')
            uri_parts = uri.split('/')
            package, everything_else = uri_parts[0], uri_parts[1:]

            expected_full_path = os.path.join(
                _app_base_dir,
                package,
                'static',
                'schemas',
                *everything_else)
            if os.path.exists(expected_full_path):
                with open(expected_full_path) as fp:
                    json_schema = json.load(fp)
                return json_schema
        except Exception:
            return super(CorJsonResolver, self).resolve_remote(uri)


class GramediaDraft4Validator(validators.Draft4Validator):
    """  JSON Schema validator.  This is the same as the default validator, for all intents and purposes.
    """
    def __init__(self, schema, resolver):
        super(GramediaDraft4Validator, self).__init__(schema, resolver=resolver)


def validate_gramedia_jsonschema(jsondoc: dict, schema: dict, base_url: str='https://gramedia.com/static/schemas/'):
    """ Validates a JSON schema using GDN's validator.  Where this differs is that it assumes any schemas that start
    with 'base_url' may be located on disk, and will try to locate them based on filename instead of via an HTTP
    url.
    """
    resolver = CorJsonResolver(base_url, jsondoc)
    GramediaDraft4Validator(schema, resolver).validate(jsondoc)
