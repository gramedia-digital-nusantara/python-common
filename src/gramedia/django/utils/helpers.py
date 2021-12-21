import io
from datetime import timedelta
from http import HTTPStatus
from urllib.parse import quote_plus

import requests
from PIL import Image
from rest_framework_simplejwt.tokens import Token


def snake_to_camel_case(value: str) -> str:
    splited_words = value.split('_')
    return ''.join(splited_words[index] if index == 0 else splited_words[index].title()
                   for index in range(len(splited_words)))


def generate_image_file(size, data):
    file = io.BytesIO()
    image = Image.frombytes('L', size, data)
    image.save(file, 'png')
    file.name = 'test.png'
    file.seek(0)
    return file


class MyToken(Token):
    token_type = 'access'
    lifetime = timedelta(days=1)


def gen_test_user_token(for_user, is_reseller=True, site='example.com'):
    test_token = MyToken.for_user(for_user)
    test_token['site'] = site
    test_token['user_id'] = for_user.username
    test_token['iss'] = 'nusantara_admin'

    return test_token


def is_valid_youtube_url(video_url: str) -> bool:
    try:
        request = requests.head(f'https://www.youtube.com/oembed?format=json&url={quote_plus(video_url)}', timeout=0.5)
        if request.status_code != HTTPStatus.OK:
            return False
    except:
        return False
    return True
