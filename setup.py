from distutils.core import setup

setup(
    name='python-common',
    version='0.2.0',
    packages=[
        'gramedia',
        'gramedia.common'
    ],
    url='https://engineering.gramedia.com',
    license='',
    author='Backend Team',
    install_requires=[
        'humanize',
    ],
    author_email='backend@staff.gramedia.com',
    description='Basic python 3.6 helper classes and functions'
)
