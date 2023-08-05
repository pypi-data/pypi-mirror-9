import os, time, compileall, sys
from setuptools import setup, find_packages

if "sdist" in sys.argv:
    path = os.path.abspath(os.path.dirname(__file__))+"\\django_vehicles_maintenance\\"
    compileall.compile_dir(path, force=True)

# README = open(os.path.join(os.path.dirname(__file__), 'README.txt')).read()
with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
    README = readme.read()
REQUIREMENTS = [i.strip() for i in open("requirements.txt").readlines()]
# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))


setup(
    name = 'django_vehicles_maintenance',
    version = '0.0.6',
    packages = ['django_vehicles_maintenance',],
    include_package_data = True,
    license = 'BSD License', # example license
    description = '`mantenimiento de vehiculos',
    long_description = README,
    url = '',
    author = 'jesus Manuel Herrera',
    author_email = 'jesusmahererra@gmail.com',
    classifiers = [
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License', # example license
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
    install_requires=REQUIREMENTS,
)
