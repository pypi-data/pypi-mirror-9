"""
Flask-Sillywalk
-------------

"""
from setuptools import setup


setup(
    name='Flask-Sillywalk',
    version='1.0.1',
    url='https://github.com/hobbeswalsh/flask-sillywalk',
    license='Unlicense',
    author='Robin Walsh',
    author_email='rob.walsh@gmail.com',
    description='So you want to implement an auto-documenting API?',
    long_description=__doc__,
    packages=['sillywalk'],
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    install_requires=[
        'Flask'
    ],
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
