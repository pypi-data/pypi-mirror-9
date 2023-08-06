from setuptools import setup

setup(name='django-simple-redis',
    version='0.0.1',
    description='simplest way to connect to redis on a django application',
    url='http://github.com/devpopol/django-simple-redis',
    author='Stephen Paul Suarez',
    author_email='devpopol@gmail.com',
    license='MIT',
    packages=['django_simple_redis'],
    install_requires=[
        'redis >= 2.9.1'
    ],
    zip_safe=True
)
