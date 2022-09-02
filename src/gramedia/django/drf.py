"""
Django Rest Framework utility classes
=====================================

Anything in this package is used along with the Django Rest Framework
to provide for our use cases within our application.
"""
import django
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site
from django.contrib.sites.shortcuts import get_current_site
from django.utils.translation import get_language_from_request
from djangorestframework_camel_case.render import CamelCaseJSONRenderer
from rest_framework import serializers
from rest_framework import pagination
from rest_framework.permissions import BasePermission
from rest_framework.response import Response
from rest_framework.utils.urls import replace_query_param
from rest_framework_simplejwt.authentication import JWTAuthentication

from rest_framework.relations import HyperlinkedRelatedField, HyperlinkedIdentityField
from rest_framework.serializers import HyperlinkedModelSerializer

from gramedia.common.http import LinkHeaderField, LinkHeaderRel
from rest_framework_simplejwt.exceptions import AuthenticationFailed
from rest_framework_simplejwt.exceptions import InvalidToken
from rest_framework_simplejwt.settings import api_settings

if django.VERSION >= (4, 0):
    from django.utils.translation import gettext_lazy as _
else:
    from django.utils.translation import ugettext_lazy as _

class LinkHeaderPagination(pagination.PageNumberPagination):
    """ Replaces the default pagination classes, provided by DRF, with one
    that returns pagination data as part of the HTTP Link header.

    The RFC can be found `here<https://www.w3.org/Protocols/9707-link-header.html>`_

    In addition, a second, custom HTTP header is included: X-Total-Results,
    which will be a numeric count of the total number of objects across all
    pages.
    """
    page_size_query_param = 'per_page'
    max_page_size = 250

    def get_first_url(self):
        if not self.page.has_previous():
            return None
        url = self.request.build_absolute_uri()
        return replace_query_param(url, self.page_query_param, 1)

    def get_last_url(self):
        if not self.page.has_next():
            return None
        url = self.request.build_absolute_uri()
        return replace_query_param(
            url, self.page_query_param, self.page.paginator.num_pages)

    def get_paginated_response(self, data):

        next_url = self.get_next_link()
        previous_url = self.get_previous_link()

        link_parts = []

        # if we have a next page, then we know we have a last, as well.
        if next_url is not None:
            link_parts.extend([
                LinkHeaderField(
                    url=next_url,
                    rel=LinkHeaderRel.next,
                    title=str(self.page.number + 1)),
                LinkHeaderField(
                    url=self.get_last_url(),
                    rel=LinkHeaderRel.last,
                    title=self.page.paginator.num_pages),
            ])

        # if we have a previous page, then we know we have a first page, too.
        if previous_url is not None:
            link_parts.extend([
                LinkHeaderField(
                    url=previous_url,
                    rel=LinkHeaderRel.prev,
                    title=str(self.page.number - 1)),
                LinkHeaderField(
                    url=self.get_first_url(),
                    rel=LinkHeaderRel.first,
                    title=str(1)),
            ])

        headers = {
            'X-Total-Results': self.page.paginator.count,
            'X-Page-Size': self.get_page_size(self.request),
            'X-Page': self.page.number
        }

        if link_parts:
            headers['Link'] = ", ".join([str(link) for link in link_parts])

        return Response(data, headers=headers)


def convert_env_boolean(env_value: str) -> bool:
    """ Converts an envvar string into a boolean.  Rules: true/True/TRUE/t/T/1 -> True;  All others false

    >>> convert_env_boolean('t')
    True

    >>> convert_env_boolean('1')
    True

    >>> convert_env_boolean('0')
    False
    """
    return env_value.lower() in ['true', '1', 't']


class SoftDeletableListViewMixin:
    """ Same as a 'ListViewMixin', but instead, by default, filters out
    models which have an 'is_active' attribute set to false.

    If the 'include_inactive=true', parameter is passed in the query string,
    then all models (regardless of 'is_active' attribute), will be returned.
    """
    def get_queryset(self):
        if convert_env_boolean(self.request.query_params.get('include_inactive', '')):
            return self.queryset
        else:
            return self.queryset.filter(is_active=True)


class IsAuthenticatedOrOptions(BasePermission):
    """ Allows access only to authenticated users, unless the request is
    for the http OPTIONS method, then the user is directly allowed.
    """
    def has_permission(self, request, view):
        if request.method == 'OPTIONS':
            return True
        else:
            return request.user and request.user.is_authenticated()


class IsOwner(BasePermission):
    def has_permission(self, request, view):
        if view.queryset.get().user == request.user:
            return True


class SummarizedListMixin:
    def get_serializer_class(self):
        if self.request.method == 'GET':
            if hasattr(self, 'summary_serializer_class'):
                return self.summary_serializer_class
            else:
                return create_summary_serializer(self.serializer_class)
        else:
            return self.serializer_class


def create_summary_serializer(serializer_cls):
    """ Creates a 'summary serializer' for a given standard serializer class.

    This is intended for list endpoints, and shortens the serializer class to only send back a 'title' and an 'href'

    :param serializer_cls:
    :return:
    """
    class SummarySerializer(serializer_cls):
        class Meta(serializer_cls.Meta):
            fields = getattr(
                serializer_cls.Meta,
                'summary_fields',
                ('href', 'name')
            )
    return SummarySerializer


class SummaryCamelCaseRenderer(CamelCaseJSONRenderer):
    """ Just like the CamelCaseJSONRenderer, but replaces any MultiLang fields (or things that
    LOOK like multilang fields) and replaces them with a string representing the user's current language.

    .. code-block:: python

        renderer.render({
            "name": "Derek",
            "bio": {
                "en": "From Pittsburgh",
                "id": "Dari Pittsburgh"
            }
        })

        # this will then return if the request language was set to english
        {
            "name": "Derek",
            "bio": "From Pittsburgh"
        }

    """
    media_type = 'application/json'
    format = 'json'

    def render(self, data, accepted_media_type=None, renderer_context=None):
        # TODO: this is ugly as sin.. needs refactored heavily.
        if isinstance(data, list):
            for element in data:
                enabled_languages = sorted([t[0] for t in settings.LANGUAGES])
                for k, v in element.items():
                    if isinstance(v, dict) and enabled_languages == sorted(v.keys()):
                        preferred_language = settings.LANGUAGE_CODE
                        try:
                            preferred_language = get_language_from_request(renderer_context['request'])
                        except Exception:
                            pass
                        element[k] = v[preferred_language[:2]]  # make if something like en-US, just get 'en'
        elif isinstance(data, dict):
            enabled_languages = sorted([t[0] for t in settings.LANGUAGES])
            for k, v in data.items():
                if isinstance(v, dict) and enabled_languages == sorted(v.keys()):
                    preferred_language = settings.LANGUAGE_CODE
                    try:
                        preferred_language = get_language_from_request(renderer_context['request'])
                    except Exception:
                        pass
                    data[k] = v[preferred_language[:2]]  # make if something like en-US, just get 'en'
        return super(SummaryCamelCaseRenderer, self).render(
            data,
            accepted_media_type=accepted_media_type,
            renderer_context=renderer_context
        )


class FullCamelCaseRenderer(CamelCaseJSONRenderer):
    media_type = 'application/json'
    format = 'json+full'


class CurrentSiteSerializerMixin:
    """ Automatically attaches the current 'site' to a model.

    .. warning::
        This is only for use with FK-Site-related models, with an attribute 'site'
    """

    def create(self, validated_data):
        validated_data['site'] = get_current_site(self.context['request'])
        return super().create(validated_data)

    def update(self, instance, validated_data):
        validated_data['site'] = get_current_site(self.context['request'])
        return super().update(instance, validated_data)


class CurrentSiteViewSetMixin:

    def get_queryset(self):
        site = get_current_site(self.request)
        return self.queryset.filter(site=site)

    @property
    def current_site(self):
        return get_current_site(self.request)


class JWTNusantaraAuthentication(JWTAuthentication):
    request = None

    def authenticate(self, request):
        header = self.get_header(request)

        if header is None:
            return None

        self.request = request

        raw_token = self.get_raw_token(header)
        if raw_token is None:
            return None

        validated_token = self.get_validated_token(raw_token)

        return self.get_user(validated_token), validated_token

    def get_user(self, validated_token):
        """
        Attempts to find and return a user using the given validated token.
        """
        try:
            user_id = validated_token[api_settings.USER_ID_CLAIM]
        except KeyError:
            raise InvalidToken(_('Token contained no recognizable user identification'))

        try:
            user_site = validated_token['site']
        except KeyError:
            raise InvalidToken(_('Token contained no recognizable site identification'))

        site = None
        if self.request:
            site = Site.objects.get_current(self.request)
        if site is None:
            raise AuthenticationFailed(_('Site not found'), code='user_not_found')
        if user_site != site.domain:
            raise AuthenticationFailed(_('Site is not match'), code='user_not_found')

        try:
            user = get_user_model().objects.get(**{api_settings.USER_ID_FIELD: user_id})
        except get_user_model().DoesNotExist:
            raise AuthenticationFailed(_('User not found'), code='user_not_found')

        if not user.is_active:
            raise AuthenticationFailed(_('User is inactive'), code='user_inactive')

        return user


def is_normal_user(request):
    if not request.user:
        return True

    if not(request.user.is_staff or request.user.is_superuser):
        return True


def get_entity_href_serializer(model_class, meta_extra_kwargs=None, *init_args, **init_kwargs):
    class EntityHrefSerializer(serializers.HyperlinkedModelSerializer):
        name = serializers.CharField(required=False)

        class Meta:
            model = model_class
            fields = ('href', 'name',)
            extra_kwargs = meta_extra_kwargs if meta_extra_kwargs is not None else {'href': {'lookup_field': 'slug', }, }

    return EntityHrefSerializer(*init_args, **init_kwargs)


class HyperlinkedSlugIdentityField(HyperlinkedIdentityField):
    def __init__(self, view_name=None, **kwargs):
        assert view_name is not None, 'The `view_name` argument is required.'
        kwargs['lookup_url_kwarg'] = 'slug'
        kwargs['lookup_field'] = 'slug'
        kwargs['read_only'] = True
        kwargs['source'] = '*'
        super().__init__(view_name, **kwargs)


class HyperlinkedSlugField(HyperlinkedRelatedField):
    lookup_field = 'slug'

    def __init__(self, view_name=None, **kwargs):
        kwargs['lookup_url_kwarg'] = 'slug'
        kwargs['lookup_field'] = 'slug'
        super().__init__(view_name, **kwargs)


class HyperlinkedSlugModelSerializer(HyperlinkedModelSerializer):
    """
        Same as the default DRF serializer, but uses 'slugs' instead of pk for the identity.
    """
    serializer_related_field = HyperlinkedSlugField
    serializer_url_field = HyperlinkedSlugIdentityField
