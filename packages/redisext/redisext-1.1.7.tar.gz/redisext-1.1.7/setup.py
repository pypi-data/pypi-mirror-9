import re
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

version = ''

with open('redisext/__init__.py', 'r') as fd:
    regex = re.compile(r'__version__\s*=\s*[\'"]([^\'"]*)[\'"]')
    for line in fd:
        m = regex.match(line)
        if m:
            version = m.group(1)
            break

setup(
    name='redisext',
    packages=['redisext', 'redisext.backend', 'redisext.models'],
    package_data={'': ['LICENSE']},
    version=version,
    description='Data models for Redis',
    author='Andrey Gubarev',
    author_email='mylokin@me.com',
    url='https://github.com/mylokin/redisext',
    keywords=['redis', 'orm', 'models'],
    license='MIT',
    classifiers=(
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4'
        'Topic :: Database',
        'Topic :: Database :: Database Engines/Servers',
    ),
)
