import base64
import io
import os
from datetime import timedelta

from PIL import Image

from rest_framework_simplejwt.tokens import Token


class MyToken(Token):
    token_type = 'access'
    lifetime = timedelta(days=1)


def gen_test_user_token(for_user, is_reseller=False, site='example.com'):
    test_token = MyToken.for_user(for_user)
    test_token['site'] = site
    test_token['user_id'] = for_user.username
    test_token['is_reseller'] = is_reseller
    test_token['iss'] = 'nusantara_admin'

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
