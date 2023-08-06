"""
Lib Pilot for flask-pilot
"""

from setuptools import setup, find_packages

__NAME__ = "Pilot-Lib"
__version__ = "0.0.13"
__author__ = "Mardix"
__license__ = "MIT"
__copyright__ = "(c) 2015 Mardix"


setup(
    name=__NAME__,
    version=__version__,
    license=__license__,
    author=__author__,
    author_email='mardix@github.com',
    description="Pilot-Lib",
    long_description=__doc__,
    url='https://github.com/mardix/flask-pilot',
    download_url='http://github.com/mardix/flask-pilot/tarball/master',
    include_package_data=True,
    packages=find_packages(),
    install_requires=[
        'Flask==0.10.1',
        'Flask-Classy==0.6.10',
        'Flask-Assets==0.10',
        'Flask-Mail==0.9.1',
        'Flask-WTF==0.11',
        'Active-SQLAlchemy==0.3.2',
        'flask-recaptcha==0.3',
        'ses-mailer',
        'passlib==1.6.2',
        'python-slugify==0.1.0',
        'PyMySQL==0.6.1',
        'flask-login==0.2.11',
        'flask-kvsession==0.6.1',
        'raven==5.0.0',
        'redis==2.9.1',
        'requests==2.2.1',
        'reversionup==0.1.2',
        'humanize==0.5.1',
        'mistune==0.5',
        'flask-s3==0.1.7'
    ],

    keywords=["pilot"],
    platforms='any',
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    zip_safe=False
)


