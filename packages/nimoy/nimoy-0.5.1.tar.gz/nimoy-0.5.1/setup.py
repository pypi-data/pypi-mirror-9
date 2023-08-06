# coding: utf-8
exec(open('nimoy/version.py').read())


from setuptools import setup

def next_version():
    _v = __version__.split('.')
    _v[-1] = str(int(_v[-1]) + 1)
    return '.'.join(_v)

def read_file(f):
    try:
        with open(f, 'r') as _file:
            return _file.read()
    except Exception as e:
        return ''

setup(
    name='nimoy',
    version=__version__,
    url='https://github.com/laco/nimoy/',
    download_url='https://github.com/laco/nimoy/tarball/' + __version__,
    license='Apache2.0',
    author='László Andrási',
    author_email='mail@laszloandrasi.com',
    description='Python3 Database Access Layer with Simple Functions and Dictionaries',
    long_description=read_file('README.md') + '\n\n',
    packages=['nimoy', 'nimoy.backends'],
    include_package_data=True,
    zip_safe=False,
    platforms='any',
    install_requires=['mongomock', 'pymongo', ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
)
