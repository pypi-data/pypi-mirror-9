# import multiprocessing to avoid this bug (http://bugs.python.org/issue15881#msg170215_
import multiprocessing
assert multiprocessing
import re
from setuptools import setup, find_packages


def get_version():
    """
    Extracts the version number from the version.py file.
    """
    VERSION_FILE = 'entity/version.py'
    mo = re.search(r'^__version__ = [\'"]([^\'"]*)[\'"]', open(VERSION_FILE, 'rt').read(), re.M)
    if mo:
        return mo.group(1)
    else:
        raise RuntimeError('Unable to find version string in {0}.'.format(VERSION_FILE))


setup(
    name='django-entity',
    version=get_version(),
    description='Entity relationship management for Django',
    long_description=open('README.md').read(),
    url='http://github.com/ambitioninc/django-entity/',
    author='Wes Kendall',
    author_email='wesleykendall@gmail.com',
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Framework :: Django',
    ],
    install_requires=[
        'Django>=1.6',
        'django-activatable-model>=0.3.0',
        'django-manager-utils>=0.7.0',
        'celery>=3.1',
        'jsonfield>=0.9.20',
    ],
    tests_require=[
        'django-dynamic-fixture',
        'django-nose',
        'mock',
        'psycopg2',
        'south>=1.0.2',
    ],
    test_suite='run_tests.run_tests',
    include_package_data=True,
    zip_safe=False,
)
