import os
from setuptools import setup

readme_path = os.path.join(os.path.dirname(
  os.path.abspath(__file__)),
  'README.rst',
)
long_description = open(readme_path).read()
version_path = os.path.join(os.path.dirname(
  os.path.abspath(__file__)),
  'VERSION',
)
version = open(version_path).read()


setup(
  name='flask-boilerplate-utils',
  version=version,
  packages=['flask_boilerplate_utils'],
  author="Nick Whyte",
  author_email='nick@nickwhyte.com',
  description="Additional functionality with easy upgrading for the flask-boilerplate.",
  long_description=long_description,
  url='https://github.com/nickw444/flask-boilerplate-utils',
  include_package_data=True,
  package_data={
    'templates':['*']
  },
  zip_safe=False,
  install_requires=[
    "Flask",
    "raven",
    "flask-wtf",
    "flask-babel",
    "flask-script",
    "meinheld",
    "flask-classy"
  ],
)
