#!/usr/bin/env python
from setuptools import setup

def readme():
    with open('README.md') as f:
        return f.read()

setup(name='django_wsgi_deployer',
      version='0.3.3',
      description='Django WSGI Project Deployer',
      long_description = readme(),
      classifiers=[
          'Development Status :: 4 - Beta',
          'Environment :: Console',
          'Framework :: Django',
          'Intended Audience :: Developers',
          'Intended Audience :: System Administrators',
          'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
          'Natural Language :: English',
          'Operating System :: POSIX',
          'Programming Language :: Python',
          'Topic :: Internet :: WWW/HTTP :: WSGI',
          'Topic :: Utilities',
      ],
      keywords = 'django wsgi apache deployment',
      url='https://github.com/evili/django_wsgi_deployer',
      author='Evili del Rio',
      author_email='evili.del.rio@gmail.com',
      license='LGPL',
      install_requires=['virtualenv', 'lockfile', 'six'],
      packages=['django_wsgi_deployer'],
      scripts=['bin/django_wsgi_deploy'],
      test_suite='nose.collector',
      tests_require=['nose','coverage'])


