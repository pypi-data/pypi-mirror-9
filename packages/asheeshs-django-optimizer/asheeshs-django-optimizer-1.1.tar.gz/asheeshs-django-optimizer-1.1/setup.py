from codecs import open
from setuptools import setup
import os


here = os.path.abspath(os.path.dirname(__file__))


# Get longdesc from file.
with open(os.path.join(here, 'README.rst'),
          encoding='utf-8') as f:
    long_description = f.read()


setup(
    name='asheeshs-django-optimizer',
    version='1.1',
    description='A pretend Django optimizer for use in a web security tutorial',
    long_description=long_description,
    author='asheesh@asheesh.org',
    license='Expat',
    classifiers = [
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
    ],
    packages=['asheeshs_django_optimizer'],
)
