import os
from setuptools import setup

with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))
PROJECT_NAME = 'seo'

setup(
    name='django-seo-admin',
    version='0.1',
    packages=[
        PROJECT_NAME,
    ],
    include_package_data=True,
    license='BSD License', 
    description='App for apply SEO on your websites with Django.',
    long_description=README,
    url='https://github.com/mapeveri/django-seo-admin',
    author='Peveri Martin',
    author_email='martinpeveri@gmail.com',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License', # example license
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        # Replace these appropriately if you are stuck on Python 2.
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
)