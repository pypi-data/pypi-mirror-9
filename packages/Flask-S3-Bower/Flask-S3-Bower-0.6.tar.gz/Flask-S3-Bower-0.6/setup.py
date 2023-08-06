"""
Flask-S3-Bower
-------------

Easily serve your static files from Amazon S3 and also provision for using Bower.
"""
from setuptools import setup

setup(
    name='Flask-S3-Bower',
    version='0.6',
    url='https://github.com/ibrahim12/flask-s3-bower',
    license='GNU',
    author='Ibrahim Rashid',
    author_email='irashid.com@gmail.com',
    description='Seamlessly serve the static files of your Flask app from Amazon S3 and also use bower for development',
    long_description=__doc__,
    packages=['flask_s3_bower',],
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    install_requires=[
        'Flask',
        'Boto>=2.5.2'
    ],
    download_url = 'https://github.com/ibrahim12/Flask-S3-Bower/tarball/0.6',
    tests_require=['nose', 'mock'],
    keywords=['flask_s3_bower', 'flask bower', 'flask s3', 'serve static file flask s3 bower'],
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: Other/Proprietary License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
