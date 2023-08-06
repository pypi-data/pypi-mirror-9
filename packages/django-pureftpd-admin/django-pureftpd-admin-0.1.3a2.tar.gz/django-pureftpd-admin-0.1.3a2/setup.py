import os

try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup, find_packages

README = open(os.path.join(os.path.dirname(__file__), 'README.rst')).read()

config = {
    'description': 'This is the web base administration interface for pureftpd server',
    'long_description': README,
    'author': 'Ivan Fedoseev',
    'url': 'https://ivanff@bitbucket.org/ivanff/django-pureftpd-admin',
    'author_email': 'agestart@gmail.com',
    'version': '0.1.3a2',
    'install_requires': ['Django', 'Mysql-python'],
    'packages': find_packages(),
    'include_package_data': True,
    'name': 'django-pureftpd-admin',
    'classifiers': [
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: System Administrators',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
    'platforms': ['any'],
}

setup(**config)