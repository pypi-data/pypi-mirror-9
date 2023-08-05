import os
from setuptools import setup, find_packages
import document_library


def read(fname):
    try:
        return open(os.path.join(os.path.dirname(__file__), fname)).read()
    except IOError:
        return ''

dependency_links = [
    # needs this dev version for django 1.6 fixes
    'https://github.com/KristianOellegaard/django-hvad/tarball/0e2101f15404eaf9611cd6cf843bfc424117b227',  # NOQA
]


setup(
    name="django-document-library",
    version=document_library.__version__,
    description=read('DESCRIPTION'),
    long_description=read('README.rst'),
    license='The MIT License',
    platforms=['OS Independent'],
    keywords='django, cms, documents, library, filer',
    author='Martin Brochhaus',
    author_email='mbrochh@gmail.com',
    url="https://github.com/bitmazk/django-document-library",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'django',
        'django-libs',
        'python-dateutil',
    ],
    dependency_links=dependency_links,
    tests_require=[
        'fabric',
        'factory_boy',
        'django-nose',
        'coverage',
        'django-coverage',
        'mock',
    ],
    test_suite='document_library.tests.runtests.runtests',
)
