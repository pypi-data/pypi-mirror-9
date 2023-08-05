"""
setup for nsupdate package
"""

import sys
PY2 = sys.version_info[0] == 2

from setuptools import setup, find_packages

from nsupdate import version

with open('README.rst') as f:
    readme_content = f.read()

if PY2:
    install_requires = ['dnspython', ]
else:
    install_requires = ['dnspython3', ]

setup(
    name='nsupdate',
    version=str(version),
    url='http://github.com/nsupdate-info/nsupdate.info/',
    license='BSD',
    author='The nsupdate.info Team (see AUTHORS)',
    author_email='info@nsupdate.info',
    description='A dynamic DNS update service',
    long_description=readme_content,
    keywords="dyndns ddns dynamic dns django",
    packages=find_packages(exclude=['_tests', ]),
    package_data={
        'nsupdate': [
            'templates/*.html',
            'templates/includes/*.html',
            'static/*.html',
            'static/*.png',
            'static/css/*.css',
            'locale/*/LC_MESSAGES/*',
        ],
        'nsupdate.accounts': [
            'templates/accounts/*.html',
            'templates/registration/*.html',
            'templates/registration/*.txt',
        ],
        'nsupdate.login': [
            'templates/*.html',
        ],
        'nsupdate.main': [
            'templates/main/*.html',
            'templates/main/includes/*.html',
        ],
    },
    include_package_data=True,
    zip_safe=False,
    platforms='any',
    install_requires=install_requires + [
        'netaddr',
        'django>=1.7.1, <1.8',
        'django-bootstrap-form',
        'django-registration-redux',
        'django-extensions',
        'python-social-auth',
        'requests',  # for our ddns_client
    ],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Django',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Topic :: Internet :: Name Service (DNS)',
    ],
)
