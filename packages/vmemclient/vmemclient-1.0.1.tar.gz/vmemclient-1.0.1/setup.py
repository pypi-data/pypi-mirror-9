import os

PKG_NAME = 'vmemclient'
EXTRA_OPTIONS = {}

# Get the best setup()
try:
    from setuptools import setup
    EXTRA_OPTIONS = {
        'zip_safe': False,
    }
except ImportError:
    from distutils.core import setup


def get_contents(*args):
    contents = []
    for parts in args:
        filename = os.path.join(*parts)
        with open(filename, 'r') as fd:
            contents.append(fd.read().strip())
    return '\n\n'.join(contents)


# setup()
setup(
    name = PKG_NAME,
    version = get_contents(
        (PKG_NAME, 'data', 'version.dat'),
    ),
    description = 'Violin Memory Client Interface Library',
    long_description = get_contents(
        ('INTRO.rst',),
        ('PRODUCTS.rst',),
        ('README.rst',),
        ('CHANGELOG.rst',),
    ),
    author = 'Violin Memory, Inc.',
    author_email = 'opensource@vmem.com',
    url = 'http://www.vmem.com',
    packages = [x.format(PKG_NAME) for x in (
        '{0}', '{0}.core', '{0}.varray',
        '{0}.vshare', '{0}.concerto',
    )],
    classifiers = [
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
    ],
    license = 'Apache Version 2.0',
    keywords = 'violin violinmemory vmem vmemclient rest',
    requires = [
    ],
    package_data = {
        PKG_NAME: [
            os.path.join('data', '*.dat'),
            os.path.join('data', '*.txt'),
        ],
    },
    **EXTRA_OPTIONS
)
