from unittest import skip, TestCase
from uuid import UUID

from unittest.mock import MagicMock

from src.gramedia.django.fields import UUIDUploadTo


def is_valid_uuid(uuid_to_test, version=4):
    """ check string is uuid (string) or not """
    try:
        uuid_obj = UUID(uuid_to_test, version=version)
    except ValueError:
        return False
    return str(uuid_obj) == uuid_to_test


class UUIDUploadToTest(TestCase):
    def setUp(self):
        self.instance = MagicMock()

    def test_success(self):
        upload_to = UUIDUploadTo('/home/ubuntu')
        self.assertIsNotNone(
            upload_to(self.instance, 'myimage.jpg')
        )

    def test_success_change_filename_to_uuid4(self):
        upload_to = UUIDUploadTo('/home/ubuntu')
        path = upload_to(self.instance, 'myimage.jpg')
        filename_without_extension = path.split('/')[-1].split('.')[0]

        self.assertTrue(
            is_valid_uuid(filename_without_extension)
        )


@skip('Not Implemented')
class SiteUploadToTest(TestCase):
    pass
