from setuptools import setup, find_packages

__version__ = 'undefined'

exec(open('ming/version.py').read())

setup(name='Ming',
      version=__version__,
      description="Bringing order to Mongo since 2009",
      long_description="""Database mapping layer for MongoDB on Python. Includes schema enforcement and some facilities for schema migration.
""",
      classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Database',
        'Topic :: Software Development :: Libraries :: Python Modules',
        ], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='mongo, pymongo',
      author='Rick Copeland',
      author_email='rick@geek.net',
      url='http://merciless.sourceforge.net',
      bugtrack_url='http://sourceforge.net/p/merciless/bugs/',
      license='MIT',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=True,
      install_requires=[
        "FormEncode >= 1.2.1",
        "pymongo>=2.4",
        "pytz",
        "six>=1.6.1"
      ],
      tests_require = [
        "nose",
        "mock >=0.8.0",
        "pytz",
        "WebOb",
        "webtest",
        # "python-spidermonkey >= 0.0.10", # required for full MIM functionality
      ],
      entry_points="""
      # -*- Entry points: -*-
      [paste.filter_factory]
      ming_autoflush=ming.odm.middleware:make_ming_autoflush_middleware
      """,
      test_suite='nose.collector'
      )
