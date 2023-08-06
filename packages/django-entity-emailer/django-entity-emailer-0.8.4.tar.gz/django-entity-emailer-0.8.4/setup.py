# import multiprocessing to avoid this bug (http://bugs.python.org/issue15881#msg170215)
import multiprocessing
assert multiprocessing
import re
from setuptools import setup, find_packages


def get_version():
    """
    Extracts the version number from the version.py file.
    """
    VERSION_FILE = 'entity_emailer/version.py'
    mo = re.search(r'^__version__ = [\'"]([^\'"]*)[\'"]', open(VERSION_FILE, 'rt').read(), re.M)
    if mo:
        return mo.group(1)
    else:
        raise RuntimeError('Unable to find version string in {0}.'.format(VERSION_FILE))


setup(
    name='django-entity-emailer',
    version=get_version(),
    description='Make emailing users easy and entity-based.',
    long_description=open('README.rst').read(),
    url='https://github.com/ambitioninc/django-entity-emailer',
    author='Erik Swanson',
    author_email='opensource@ambition.com',
    keywords='',
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Framework :: Django',
        'Framework :: Django :: 1.6',
        'Framework :: Django :: 1.7',
    ],
    license='MIT',
    install_requires=[
        'beautifulsoup4>=4.3.2',
        'Django>=1.6',
        'django-db-mutex>=0.1.8',
        'django-entity>=1.8.2',
        'django-entity-event>=0.3.2',
        'django-uuidfield>=0.5.0',
        'celery>=3.1',
    ],
    tests_require=[
        'django-dynamic-fixture',
        'django-nose',
        'freezegun',
        'mock',
        'south>=1.0.2',
    ],
    test_suite='run_tests.run_tests',
    include_package_data=True,
)
