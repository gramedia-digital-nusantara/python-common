import json
import os

from jsonschema import RefResolver, validators, RefResolutionError
from jsonschema.compat import urlsplit, urldefrag


def find_schema_path(schema_name: str):
    """ Reference resolver for Django based projects.

    This assumes the following:

    - Each 'app' within your django project will have a static/schema directory, and schemas will be stored within
      that directory.
    - Your schemas will not be nested any deeper than <app>/static/schemas/<someschema.json>

    Example:
    # this file exists
    banners/static/schemas/banner-schema.json

    find_schema_path('banner_schema.json')
    > /the-full-path/banners/static/schemas/banner-schema.json

    find_schema_path('i-dont-exist.json')
    > None
    """
    try:
        from django.conf import settings
    except ImportError:
        raise RuntimeError(
            "It doesn't look like you have django installed.  "
            "You cannot use this DjangoSchemaResolver outside of a Django project.")

    for pkg in settings.INSTALLED_APPS:
        full_path = os.path.join(settings.BASE_DIR, *pkg.split('.'), 'static', 'schemas', schema_name)
        if os.path.exists(full_path):
            return full_path


class DjangoSchemaResolver(RefResolver):
    """ Reference resolver for Django based projects.

    This assumes the following:

    - Each 'app' within your django project will have a static/schema directory, and schemas will be stored within
      that directory.
    - Your schemas will not be nested any deeper than <app>/static/schemas/<someschema.json>

    Example:
    banners/static/schemas/banner-schema.json
    """

    def resolve_from_url(self, uri):
        uri, fragment = urldefrag(uri)
        split_url = urlsplit(uri)
        if split_url.scheme in self.handlers:
            return self.handlers[split_url.scheme](uri)
        full_path = find_schema_path(uri.split('/')[-1])
        if full_path:
            with open(full_path) as fp:
                json_schema = json.load(fp)
            if not json_schema:
                # TODO: fix exception method
                raise RefResolutionError(
                    "Unresolvable JSON schema: %r" % uri
                )
            return self.resolve_fragment(json_schema, fragment)
        else:
            # if a schema can't be found locally, just default to using the standard resolver
            return super(DjangoSchemaResolver, self).resolve_from_url(uri)


class DjangoDraft4Validator(validators.Draft4Validator):
    def __init__(self, schema, resolver):
        super(DjangoDraft4Validator, self).__init__(schema, resolver=resolver)
