from setuptools import setup, find_packages
import sys, os

version = '0.0.1'

setup(name='django-wechat',
      version=version,
      description="a django package with wechat api support",
      long_description="""
      a django lackage with wechat api support and a simple wechat robot
      """,
      classifiers=[
            "Development Status :: 1 - Planning",
            "Environment :: Web Environment",
            "Framework :: Django",
            "Intended Audience :: Developers",
            "License :: OSI Approved :: MIT License",
            "Natural Language :: English",
            "Operating System :: POSIX",
            "Programming Language :: Python :: 2.7",
            "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
      ], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='django-wechat, django, wechat',
      author='younger shen',
      author_email='younger.x.shen@gmail.com',
      url='https://github.com/youngershen/django-wechat',
      license='MIT',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=True,
      install_requires=[
          # -*- Extra requirements: -*-
            'django>=1.7.0'
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      test_suite="wechat.test",
      tests_require=["pyflakes>=0.6.1", "pep8>=1.4.1"],
      )
