import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.md')).read()
VERSION = open(os.path.join(here, 'VERSION')).read()

install_requires = [
    'pyramid',
    'tempita',
    'requests',
    'simplejson',
    'elasticsearch',
    'blinker'
]

setup(
    name='nefertari',
    version=VERSION,
    description='nefertari',
    long_description=README,
    classifiers=[
        "Programming Language :: Python",
        "Framework :: Pyramid",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
    ],
    author='',
    author_email='',
    url='',
    keywords='web wsgi bfg pylons pyramid rest',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    test_suite='nefertari',
    install_requires=install_requires,
    entry_points="""\
    [console_scripts]
        nefertari.index = nefertari.scripts.es:main
    """,
)
