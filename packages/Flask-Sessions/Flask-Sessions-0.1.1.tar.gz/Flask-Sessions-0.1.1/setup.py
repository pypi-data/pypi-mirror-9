"""
Flask-Session
-------------

Flask-Session is an extension for Flask that adds support for
Server-side Session to your application.

Links
`````

* `development version
  <https://github.com/fengsp/flask-session/zipball/master#egg=Flask-dev>`_

"""
from setuptools import setup


setup(
    name='Flask-Sessions',
    version='0.1.1',
    url='https://github.com/jefurry/flask-sessions',
    license='BSD',
    author='Jefurry',
    author_email='jefurry@qq.com',
    description='Adds server-side session support to your Flask application',
    long_description=__doc__,
    packages=['flask_sessions'],
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    install_requires=[
        'Flask>=0.8'
    ],
    test_suite='test_session',
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
