import os
from setuptools import setup

with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='nre-darwin-py',
    version='0.1.3',
    packages=['nredarwin'],
    install_requires=[
        'suds-jurko'
    ],
    include_package_data=True,
    license='BSD License',
    description='A simple python wrapper around National Rail Enquires LDBS SOAP Webservice',
    long_description=README,
    url='https://github.com/robert-b-clarke/nre-darwin-py',
    author='Robert Clarke',
    author_email='rob@redanorak.co.uk',
    test_suite='test_nredarwin',
    classifiers=[
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License', # example license
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Development Status :: 4 - Beta'
    ],
)
