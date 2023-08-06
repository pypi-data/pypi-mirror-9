import os
from setuptools import setup

here = os.path.dirname(os.path.abspath(__file__))

setup(
    name='pymza',
    version='0.7.17',
    author="Sergey Kirillov",
    author_email="sergey.kirillov@gmail.com",
    description="Streaming data processing framework inspired by Apache Samza.",
    packages=['pymza', 'pymza.testing'],
    install_requires=[
        'Click',
        'gevent',
        'kafka-python>=0.9.3',
        'leveldb',
        'cached_property',
    ],
    entry_points='''
        [console_scripts]
        pymza=pymza.cli:main
    ''',
    url='https://bitbucket.org/rushman/pymza',
    long_description=open(os.path.join(here, 'README.rst'), 'rb').read().decode('utf-8')
)
