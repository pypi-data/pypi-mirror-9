from setuptools import setup

import pyredis

setup(
    name='python_redis',
    version='0.0.1',
    description='Implementation of PEP 3143, a unix daemon',
    long_description=pyredis.__doc__,
    packages=['pyredis'],
    url='https://github.com/schlitzered/pyredis',
    license='MIT',
    author='schlitzer',
    author_email='stephan.schultchen@gmail.com',
    test_suite='test',
    platforms='posix',
    classifiers=[
            'License :: OSI Approved :: MIT License',
            'Programming Language :: Python :: 3'
    ],
    keywords=[
        'redis'
    ]
)