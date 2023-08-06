import os, time, compileall
from setuptools import setup,find_packages

path = os.path.abspath(os.path.dirname(__file__))+"\\djmicrosip_inventarios\\"
compileall.compile_dir(path, force=True)

with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
    README = readme.read()
REQUIREMENTS = [i.strip() for i in open("requirements.txt").readlines()]
# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

VERSION = '1.0.7'
setup(
    name = 'djmicrosip_inventarios',
    version = VERSION,
    packages = ['djmicrosip_inventarios'],
    include_package_data = True,
    license = 'BSD License', # example license
    description = 'django microsip inventarios fisicos',
    long_description = 'README',
    url = '',
    author = 'Servicios de Ingenieria Computacional',
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
