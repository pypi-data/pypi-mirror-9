import os
from setuptools import setup

with open(os.path.join(os.path.dirname(__file__), 'README.md')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='django-allauth-intersis',
    version='0.5.3',
    packages=['allauth_intersis'],
    include_package_data=True,
    license='GNU General Public License v3 (GPLv3)',
    description='OAuth2.0 InterSIS access module for projects using django-allauth.',
    long_description=README,
    url='http://www.intersis.org/',
    author='InterSIS',
    author_email='dev@intersis.org',
    install_requires=[
        'django>=1.7',
        'django-allauth>=0.19.0'
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
)
