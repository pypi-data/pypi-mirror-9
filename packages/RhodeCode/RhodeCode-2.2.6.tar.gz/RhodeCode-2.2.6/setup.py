# -*- coding: utf-8 -*-
import os
import sys
from setuptools import setup
from setuptools.command.install import install


requirements = [
]

dependency_links = [
]

classifiers = [
    'Development Status :: 6 - Mature',
    'Environment :: Web Environment',
    'Framework :: Pylons',
    'Intended Audience :: Developers',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Programming Language :: Python :: 2.5',
    'Programming Language :: Python :: 2.6',
    'Programming Language :: Python :: 2.7',
]


# additional files from project that goes somewhere in the filesystem
# relative to sys.prefix
data_files = []

# additional files that goes into package itself
package_data = {'rhodecode': ['i18n/*/LC_MESSAGES/*.mo', ], }

description = ('RhodeCode is a fast and powerful management tool '
               'for Mercurial and GIT with a built in push/pull server, '
               'full text search and code-review.')

keywords = ' '.join([
    'rhodecode', 'rhodiumcode', 'mercurial', 'git', 'code review',
    'repo groups', 'ldap', 'repository management', 'hgweb replacement',
    'hgwebdir', 'gitweb replacement', 'serving hgweb',
])



class MyInstall(install):
    def run(self):
        install.run(self)
        print """
        ***************************** IMPORTANT *****************************
        RhodeCode installation via pypi is deprecated.
        In order to maximize user experience we have launched a new
        cross platform installer. Please contact us via support@rhodecode.com
        for more information, or visit https://docs.rhodecode.com for
        latest installation instructions.
        ***************************** IMPORTANT *****************************
        """

setup(
    name='RhodeCode',
    version='2.2.6',
    description=description,
    long_description=description,
    keywords=keywords,
    author='RhodeCode GmbH',
    author_email='marcin@rhodecode.com',
    dependency_links=dependency_links,
    url='https://rhodecode.com',
    install_requires=requirements,
    classifiers=classifiers,
    setup_requires=[],
    data_files=data_files,
    packages=[],
    include_package_data=True,
    package_data=package_data,
    zip_safe=False,
    cmdclass={'install': MyInstall},
)


