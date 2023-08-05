from setuptools import setup


setup(
    name='Flask-qiniu',
    version='1.1.3',
    url='https://github.com/humiaozuzu/flask-qiniu',
    license='BSD',
    author='Miao Hu',
    author_email='maplevalley8@gmail.com',
    description='Flask Qiniu extension',
    long_description=__doc__,
    py_modules=['flask_qiniu'],
    # if you would be using a package instead use packages instead
    # of py_modules:
    # packages=['flask_sqlite3'],
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    install_requires=[
        'Flask',
        'qiniu',
        'requests'
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
