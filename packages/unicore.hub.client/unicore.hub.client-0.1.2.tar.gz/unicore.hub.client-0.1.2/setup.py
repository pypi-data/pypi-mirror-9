import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.rst')) as f:
    README = f.read()

with open(os.path.join(here, 'requirements.txt')) as f:
    requires = filter(None, f.readlines())

with open(os.path.join(here, 'VERSION')) as f:
    version = f.read().strip()

setup(name='unicore.hub.client',
      version=version,
      description='Client library to interact with Universal '
                  'Core\'s unicore.hub',
      long_description=README,
      classifiers=[
          "Programming Language :: Python",
          "Topic :: Internet :: WWW/HTTP",
          "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
      ],
      author='Praekelt Foundation',
      author_email='dev@praekelt.com',
      url='http://github.com/universalcore/unicore.hub.client',
      license='BSD',
      keywords='authentication, user, universal, core',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      namespace_packages=['unicore'],
      install_requires=requires,
      tests_require=requires)
