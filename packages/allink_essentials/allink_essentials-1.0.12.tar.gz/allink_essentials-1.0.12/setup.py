#! /usr/bin/env python
from setuptools import setup

import allink_essentials
setup(
    name='allink_essentials',
    version=allink_essentials.__version__,
    description='collection of code fragments',
    long_description='collection of code fragments',
    author='Marc Egli',
    author_email='egli@allink.ch',
    url='http://github.com/allink/allink-essentials/',
    license='BSD License',
    platforms=['OS Independent'],
    packages=[
        'allink_essentials',
        'allink_essentials.analytics',
        'allink_essentials.analytics.templatetags',
        'allink_essentials.fabfiles',
        'allink_essentials.feincms_extensions',
        'allink_essentials.logging',
        'allink_essentials.in_footer',
        'allink_essentials.in_footer.templatetags',
        'allink_essentials.mailchimp_api',
        'allink_essentials.middleware',
        'allink_essentials.storage',
        'allink_essentials.view',
        'allink_essentials.search',
    ],
    # package_data={'allink_essentials':'templates/*.html'},
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Communications :: Email',
    ],
    requires=[
    ],
    include_package_data=True,
)
