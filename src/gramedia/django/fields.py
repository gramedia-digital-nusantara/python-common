import os
import uuid

from django.contrib.sites.models import Site
from django.utils.deconstruct import deconstructible


##
# Upload To
##
@deconstructible
class UUIDUploadTo:
    """
    Automatically change name of file to uuid
    > my-uploaded-file.png
    >> e1f19c9d-2a40-4a8c-af32-61dfc1c94e25.png

    How to:
    class Gallery(models.Model):
        # result: media/e1f19c9d-2a40-4a8c-af32-61dfc1c94e25.png
        file = models.FileField(upload_to=UUIDUploadTo('media'))
    """
    def __init__(self, path):
        self.path = path

    def __call__(self, instance, filename):
        path = os.path.join(self.path, "%s%s")
        # @note It's up to the validators to check if it's the correct file type in name or if one even exist.
        extension = os.path.splitext(filename)[1]
        return path % (uuid.uuid4(), extension)


@deconstructible
class SiteUploadTo(UUIDUploadTo):
    """
    Automatically change name of file to uuid and add it in domain folder name.

    How to:
    class Gallery(models.Model):
        # result: example.com/media/e1f19c9d-2a40-4a8c-af32-61dfc1c94e25.png
        file = models.FileField(
            upload_to=SiteUploadTo('media', site_location=['user', 'site'])
        )
        user = models.Foreign('users.User', on_delete=models.CASCADE))
    """
    def __init__(self, path, site_location):
        self.path = path
        self.site_location = site_location or []

    def __call__(self, instance, filename):
        if self.site_location and isinstance(self.site_location, list):
            result = instance
            for location_path in self.site_location:
                related_instance = getattr(result, location_path, None)
                if related_instance:
                    result = related_instance

            if not isinstance(result, Site):
                raise ValueError('last result from site_location is\'nt site instance')

            self.path = os.path.join(self.path, result.domain)

        return super().__call__(instance, filename)
