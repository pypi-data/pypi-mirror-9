try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name='redisext',
    packages=['redisext', 'redisext.backend', 'redisext.models'],
    version='1.1.2',
    description='Data models for Redis',
    author='Andrey Gubarev',
    author_email='mylokin@me.com',
    url='https://github.com/mylokin/redisext',
    keywords=['redis', 'orm', 'models'],
    classifiers=(
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4'
    ),
)
