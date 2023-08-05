import os, time, compileall, sys
from setuptools import setup, find_packages

if "sdist" in sys.argv:
	path = os.path.abspath(os.path.dirname(__file__))+"\\django_microsip_base\\"
	compileall.compile_dir(path, force=True)

with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
    README = readme.read()
# this grabs the requirements from requirements.txt
REQUIREMENTS = [i.strip() for i in open("requirements.txt").readlines()]
# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
  name = 'django-microsip-base',
  version ='0.2.4',
  packages = find_packages(),
  include_package_data = True,
  description = "Django Microsip Base",
  long_description = README,
  author = "Servicios de Ingenieria Computacional",
  author_email = "jesusmaherrera@gmail.com",
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