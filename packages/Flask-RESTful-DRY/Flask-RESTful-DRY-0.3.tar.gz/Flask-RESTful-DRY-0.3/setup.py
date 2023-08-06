# setup.py

###  Assume that this is already provided in Python 3.4
###
###  ez_setup.py is included in this repository:
### from ez_setup import use_setuptools
### use_setuptools()

from setuptools import setup, find_packages, Command


class PyTest(Command):
    user_options = []
    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        import sys,subprocess
        errno = subprocess.call(['py.test'])
        raise SystemExit(errno)

with open('README.rst', 'rt') as f:
    long_description = f.read()

setup(
    name="Flask-RESTful-DRY",
    version="0.3",
    author = "Bruce Frederiksen",
    author_email = "dangyogi@gmail.com",
    description = "DRY applied to Flask-RESTful by using declarations, "
                  "not code",
    long_description = long_description,
    url = "https://bitbucket.org/dangyogi/flask-restful-dry",
    license = 'MIT',
    keywords = 'Flask RESTful Flask-RESTful DRY declarations web',
    classifiers = [
      'Development Status :: 2 - Pre-Alpha',
      'Framework :: Flask',
      'Intended Audience :: Developers',
      'License :: OSI Approved :: MIT License',
      'Operating System :: OS Independent',
      'Programming Language :: Python :: 3.4',
    ],

    include_package_data=True,
    zip_safe=False,
    packages=find_packages(),
    install_requires=[
        "flask >= 0.10.1",
        "Flask-Login >= 0.2.11",
        "Flask-RESTful >= 0.2.12",
        "Flask-WTF >= 0.10.0",
        "Flask-SQLAlchemy >= 1.0",
        "SQLAlchemy >= 0.9.7",
        "passlib >= 1.6.2",

        # These should be deleted:
        #"Flask-Mail >= 0.9.0",
        #"Flask-Migrate >= 1.2.0",
        #"Flask-Script >= 2.0.5",
        #"psycopg2 >= 2.5.3",

        # from tests_require
        "pytest >= 2.6.1",

        "Sphinx >= 1.2.2",
    ],

    # This doesn't seem to work, so I'm adding this to install_requires too...
    tests_require=[
        "pytest >= 2.6.1",
    ],

    cmdclass = {'test': PyTest},
)
