# todo: this test case needs to be improved to match our codebase..
# from django.test import TestCase

# from transman.dispatch.models import Commodity
# from utils.http import LinkHeaderParser, LinkHeaderRel


# class LinkPaginationTests(TestCase):
#
#     def setUp(self):
#         # NOTE: this test depends on project pagination being set at 50..
#         #   maybe it would be a good idea to override the config for this
#         #   test only.
#         for _ in range(1000):
#             c = Commodity(name="something", description="else")
#             c.save()
#
#         self.response = self.client.get("/api/company/commodities?page=5")
#         self.link_header = LinkHeaderParser(self.response['link'])
#
#     def test_next(self):
#         next_link = self.link_header.get(LinkHeaderRel.next)
#         self.assertTrue(next_link.url.endswith("/api/company/commodities?page=6"))
#
#     def test_prev(self):
#         prev_link = self.link_header.get(LinkHeaderRel.prev)
#         self.assertTrue(prev_link.url.endswith("/api/company/commodities?page=4"))
#
#     def test_first(self):
#         first_link = self.link_header.get(LinkHeaderRel.first)
#         self.assertTrue(first_link.url.endswith("/api/company/commodities?page=1"))
#
#     def test_last(self):
#         last_link = self.link_header.get(LinkHeaderRel.last)
#         self.assertTrue(last_link.url.endswith("/api/company/commodities?page=20"))
#
#     def test_custom_x_headers(self):
#         self.assertIn('X-Total-Results', self.response)
#         self.assertEqual(int(self.response['X-Total-Results']), 1000)
