"""
Generic HTTP Utilities
======================

Helper classes to make working with HTTP-related headers a little bit easier.
"""
from enum import Enum
import re


class LinkHeaderRel(Enum):
    """ Simple enum that represents some basic 'rel' types that we might
    expect for a 'link header'.

    This is, by no means, comprehensive and is not intended to be.
    """
    first = 'first'
    next = 'next'
    prev = 'prev'
    last = 'last'


class LinkHeaderField(object):
    """ A single entity from a link header field.
    """
    def __init__(self, url: str, rel: LinkHeaderRel, title: str=None):
        self.url = url
        self.rel = rel
        self.title = title

    @classmethod
    def from_string(cls, link_header_part: str):
        return LinkHeaderField(
            url=LinkHeaderField._parse_url(link_header_part),
            rel=LinkHeaderField._parse_rel(link_header_part),
            title=LinkHeaderField._parse_title(link_header_part),
        )

    @staticmethod
    def _parse_rel(link_header_part):
        m = re.search(r';\srel="(?P<rel>\w+)"(;|$)', link_header_part, re.IGNORECASE)
        try:
            rel_str = m.groupdict().get('rel')
            return LinkHeaderRel(rel_str)
        except (ValueError, AttributeError):
            raise MalformedLinkHeader(f"HTTP Link Header missing/malformed 'rel': {link_header_part}")

    @staticmethod
    def _parse_url(link_header_part: str) -> str:
        m = re.search(r'^<(?P<url>.+)>', link_header_part, re.IGNORECASE)
        try:
            return m.groupdict().get('url')
        except AttributeError:
            raise MalformedLinkHeader(f"Invalid format for HTTP Link Header: {link_header_part}.")

    @staticmethod
    def _parse_title(link_header_part: str) -> str:
        m = re.search(r';\stitle="(?P<title>.+)"(;|$)', link_header_part, re.IGNORECASE)
        return m.groupdict().get('title') if m is not None else None

    def __eq__(self, other) -> bool:
        props = ['rel', 'url', 'title', ]
        return all([getattr(self, p) == getattr(other, p) for p in props])

    def __str__(self) -> str:
        link = f'<{self.url}>'
        if self.rel:
            link += f'; rel="{self.rel.value}"' if hasattr(self.rel, 'value') else f'; rel="{self.rel}"'
        link += f'; title="{self.title}"' if self.title else ""
        return link


class LinkHeaderParser(object):
    """ Parses the value of an HTTP Link header, and stores them as a set of
    `LinkHeaderField` objects under the .links attribute.
    """
    def __init__(self, link_header_complete: str):
        """
        :param `str` link_header_complete:
            The complete, unparsed value of an HTTP Link header.
        """
        self.links = [LinkHeaderField.from_string(link.strip()) for link
                      in link_header_complete.split(',')]

    def get(self, link_rel:LinkHeaderRel) -> LinkHeaderField:
        """ Fetches a single `LinkHeaderField`, matching the requested 'rel'

        If no match can be found, returns None.

        :param `LinkHeaderRel` link_rel:
        :return: The link header matching the provided `rel`
        """
        links = [link for link in self.links if link.rel == link_rel]
        return links[0] if links else None


class MalformedLinkHeader(Exception):
    """ Raised when an HTTP link header is in an invalid format.
    """
    pass
