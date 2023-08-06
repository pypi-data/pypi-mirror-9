from setuptools import setup, find_packages

import os

from os.path import dirname, realpath
from taggit_templatetags2 import __version__ as VERSION


__dir__ = realpath(dirname(__file__))

TESTS_REQUIRE = [
    'django-easytests >= 0.9.4',
    'coverage >= 3.7',
    'django-coverage >= 1.2',
    'tox >= 1.7']

setup(
    name='django-taggit-templatetags2',
    version=".".join([str(v) for v in VERSION]),
    description="Templatetags for django-taggit.",
    long_description=open(os.path.join(os.path.dirname(__file__),
                                       'README.rst')).read(),
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Framework :: Django',
    ],  # strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
    keywords='django taggit tags tagcloud taglist tagging tag',
    author='Wojciech Banas',
    author_email='fizista@gmail.com',
    url='https://github.com/fizista/django-taggit-templatetags2',
    license='BSD',
    packages=find_packages(),
    include_package_data=True,
    #     package_data={
    # If any package contains *.txt or *.rst files, include them:
    #         'taggit_templatetags2': [
    #             'templates/*',
    #             'static/*',],
    #     },
    zip_safe=False,
    install_requires=[
        'django >= 1.5',
        'django-taggit >= 0.12',
        'django-classy-tags >= 0.5.1',
    ],
    test_suite="runtests.runtests",
    tests_require=TESTS_REQUIRE,
    extras_require={
        'test': TESTS_REQUIRE,
    },

)
