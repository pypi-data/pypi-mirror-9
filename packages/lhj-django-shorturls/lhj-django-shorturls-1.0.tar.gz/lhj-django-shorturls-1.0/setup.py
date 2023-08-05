from setuptools import setup, find_packages

setup(
    name = "lhj-django-shorturls",
    version = "1.0",
    url = 'http://github.com/jacobian/django-shorturls',
    license = 'BSD',
    description = "A short URL handler for Django apps.",
    author = 'ironhoop',
    author_email = 'andrew.lhj@gmail.com',
    packages = find_packages('shorturls'),
    package_dir = {'': 'shorturls'},
    install_requires = ['setuptools'],
)
