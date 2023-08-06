from setuptools import setup
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='event-store',
    
    # Relevant: https://packaging.python.org/en/latest/single_source_version.html
    version='1.0.1a4',
    
    description='Event Store implemented in Python',
    long_description=long_description,

    url='https://bitbucket.org/drozdyuk/event-store',

    author='Andriy Drozdyuk',
    author_email='drozzy@gmail.com',

    license='Apache 2.0',

    # See: https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries',
        'License :: OSI Approved :: Apache Software License',

        'Programming Language :: Python :: 2'
    ],

    keywords='eventstore eventsourcing',

    packages=[
        'event_store',
        'event_store.application',
        'event_store.domain',
        'event_store.domain.model',
        'event_store.infrastructure',
        'event_store.infrastructure.configuration',
        'event_store.infrastructure.persistence',
        'event_store.infrastructure.persistence.schema',
        'event_store.infrastructure.reflection',
        'event_store.infrastructure.scripts',

    ],

    install_requires=['sqlalchemy>=0.9.8',
                      'psycopg2>=2.5.3'],
                      
    # You can install these using the following syntax:
    # $ pip install -e .[test]
    extras_require={
        'test': ['fake-factory']
    },

    entry_points={
        'console_scripts': [
            'event_store = event_store.infrastructure.scripts.main:main'
        ]
    }


)
