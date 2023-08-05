#!/usr/bin/env python

import os

from setuptools import setup, find_packages

try:
    # Workaround for http://bugs.python.org/issue15881
    import multiprocessing
except ImportError:
    pass

VERSION = '0.1.6'

if __name__ == '__main__':
    setup(
        name='django-datastream',
        version=VERSION,
        description="Django HTTP interface to Datastream API time-series library.",
        long_description=open(os.path.join(os.path.dirname(__file__), 'README.rst')).read(),
        author='wlan slovenija',
        author_email='open@wlan-si.net',
        url='https://github.com/wlanslovenija/django-datastream',
        license='AGPLv3',
        packages=find_packages(exclude=('*.tests', '*.tests.*', 'tests.*', 'tests')),
        package_data={},
        classifiers=[
            'Development Status :: 4 - Beta',
            'Environment :: Web Environment',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: GNU Affero General Public License v3',
            'Operating System :: OS Independent',
            'Programming Language :: Python',
            'Framework :: Django',
        ],
        include_package_data=True,
        zip_safe=False,
        dependency_links = [
            'https://github.com/wlanslovenija/ultrajson/tarball/a8f0f0f1010956b27bf0c2cb5e52d85bb84e273a#egg=ujson-1.34',
        ],
        install_requires=[
            'Django>=1.5',
            'datastream>=0.4.1',
            'django-tastypie>=0.9.16',
            'ujson==1.34',
            'pytz>=2012h',
            'mimeparse>=0.1.3',
        ],
        test_suite='tests.runtests.runtests',
    )
