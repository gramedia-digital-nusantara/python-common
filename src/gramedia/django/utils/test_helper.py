import base64
import io
import os
from datetime import timedelta

from PIL import Image

from rest_framework_simplejwt.tokens import Token


class MyToken(Token):
    token_type = 'access'
    lifetime = timedelta(days=1)


def gen_test_user_token(for_user, is_reseller=False, site='example.com', is_pos=False, warehouses=None):
    test_token = MyToken.for_user(for_user)
    test_token['site'] = site
    test_token['user_id'] = for_user.username
    test_token['is_reseller'] = is_reseller
    test_token['iss'] = 'nusantara_admin'
    test_token['is_staff'] = for_user.is_staff
    test_token['can_use_pos'] = is_pos
    test_token['warehouses'] = [] if warehouses is None else warehouses

    return test_token


def generate_image_file(size, data):
    file = io.BytesIO()
    image = Image.frombytes('L', size, data)
    image.save(file, 'png')
    file.name = 'test.png'
    file.seek(0)
    return file


def generate_base64_image(size: tuple):
    x, y = size
    image = generate_image_file(size, os.urandom(x * y))

    return base64.b64encode(image.read()).decode()
