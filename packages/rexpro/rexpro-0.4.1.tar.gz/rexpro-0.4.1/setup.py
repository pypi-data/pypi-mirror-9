import sys
from setuptools import setup, find_packages

#next time:
#python setup.py register
#python setup.py sdist upload

#import rexpro
#version = rexpro.__version__
version = open('rexpro/VERSION', 'r').readline().strip()


long_desc = """
Python RexPro interface
"""

setup(
    name='rexpro',
    version=version,
    description='Python RexPro interface',
    dependency_links=['https://github.com/platinummonkey/rexpro-python/archive/{0}.tar.gz#egg=rexpro-python-{0}'.format(version)],
    long_description=long_desc,
    classifiers=[
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        'Topic :: Database',
        'Topic :: Database :: Front-Ends',
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords='rexster,tinkerpop,rexpro,graphdb',
    install_requires=['msgpack-python>=0.4.0', 'six==1.6.1'],
    extras_require={
        'develop': ['nose==1.3.0', 'coverage==3.7.1', 'tox==1.7.1', 'celery==3.1.11', 'redis==2.9.1', 'tox>=1.7.1',
                    'detox>=0.9.3', 'gevent>=1.0', 'eventlet>=0.14.0', 'Sphinx>=1.2.2', 'watchdog>=0.7.1',
                    'sphinx-rtd-theme>=0.1.6'],
        'gevent': ['gevent>=1.0', ],
        'eventlet': ['eventlet>=0.14.0', ],
        'docs': ['Sphinx>=1.2.2', 'watchdog>=0.7.1', 'sphinx-rtd-theme>=0.1.6']
    },
    scripts=['run_coverage.sh', 'doc_builder.sh'],
    author='Blake Eggleston',
    author_email='bdeggleston@gmail.com',
    maintainer='Cody Lee',
    maintainer_email='codylee@wellaware.us',
    url='https://github.com/platinummonkey/rexpro-python',
    license='BSD',
    packages=find_packages(),
    include_package_data=True,
)
