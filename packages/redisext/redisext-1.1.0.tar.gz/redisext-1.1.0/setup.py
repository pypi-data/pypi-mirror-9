try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name='redisext',
    packages=['redisext', 'redisext.backend'],
    version='1.1.0',
    description='Data models for Redis',
    author='Andrey Gubarev',
    author_email='mylokin@me.com',
    url='https://github.com/mylokin/redisext',
    keywords=['redis', 'orm', 'models'],
    classifiers=[],
)
