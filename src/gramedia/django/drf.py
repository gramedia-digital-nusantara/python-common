"""
Django Rest Framework utility classes
=====================================

Anything in this package is used along with the Django Rest Framework
to provide for our use cases within our application.
"""
from django.conf import settings
from django.utils.translation import get_language_from_request
from djangorestframework_camel_case.render import CamelCaseJSONRenderer
from rest_framework import pagination
from rest_framework.permissions import BasePermission
from rest_framework.response import Response
from rest_framework.utils.urls import replace_query_param

from gramedia.common.http import LinkHeaderField, LinkHeaderRel


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
            'X-Page-Size': self.page_size,
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

