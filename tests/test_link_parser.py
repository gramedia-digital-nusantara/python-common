from unittest import TestCase

from gramedia.common.http import LinkHeaderField, LinkHeaderRel, MalformedLinkHeader, LinkHeaderParser


class LinkHeaderParserTests(TestCase):

    def test_complete(self):
        parser = LinkHeaderParser(LINK_HEADER_COMPLETE)
        expected_links = [LinkHeaderField.from_string(link.strip()) for link
                          in LINK_HEADER_COMPLETE.split(',')]
        expected_links.sort(key=lambda e: e.url)

        actual_links = parser.links[:]
        actual_links.sort(key=lambda e: e.url)

        self.assertListEqual(expected_links, actual_links)

    def test_get_individual(self):
        parser = LinkHeaderParser(LINK_HEADER_COMPLETE)
        first = parser.get(link_rel=LinkHeaderRel.first)
        self.assertEqual(first.rel, LinkHeaderRel.first)


class LinkHeaderFieldTests(TestCase):

    def test_url(self):
        field = LinkHeaderField.from_string(LINK_HEADER_LAST)
        self.assertEqual(field.url, 'https://api.github.com/search/code?q=addClass+user%3Amozilla&page=34')

    def test_rel(self):
        field = LinkHeaderField.from_string(LINK_HEADER_LAST)
        self.assertEqual(field.rel, LinkHeaderRel.last)

    def test_title(self):
        field = LinkHeaderField.from_string(LINK_HEADER_NEXT)
        self.assertEqual(field.title, "The Next Page")

    def test_sad_no_url(self):
        self.assertRaises(
            MalformedLinkHeader,
            lambda: LinkHeaderField.from_string('Oh fuck.. I am malformed; rel="next"'))

    def test_sad_no_rel(self):
        self.assertRaises(
            MalformedLinkHeader,
            lambda: LinkHeaderField.from_string("<http://google.com>; meh=I am still malformed"))

    def test_stringification_no_title(self):
        field = LinkHeaderField.from_string(LINK_HEADER_LAST)
        self.assertEqual(str(field), LINK_HEADER_LAST)

    def test_stringification(self):
        field = LinkHeaderField.from_string(LINK_HEADER_NEXT)
        self.assertEqual(str(field), LINK_HEADER_NEXT)

LINK_HEADER_NEXT = '<https://api.github.com/search/code?q=addClass+user%3Amozilla&page=15>; rel="next"; title="The Next Page"'
LINK_HEADER_LAST = '<https://api.github.com/search/code?q=addClass+user%3Amozilla&page=34>; rel="last"'

LINK_HEADER_COMPLETE = (
    '<https://api.github.com/search/code?q=addClass+user%3Amozilla&page=15>; rel="next", '
    '<https://api.github.com/search/code?q=addClass+user%3Amozilla&page=34>; rel="last", '
    '<https://api.github.com/search/code?q=addClass+user%3Amozilla&page=1>; rel="first", '
    '<https://api.github.com/search/code?q=addClass+user%3Amozilla&page=13>; rel="prev"')
