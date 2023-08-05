import os
from setuptools import setup
VERSION='2.3.0.7'
with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='django-marionettejs',
    version=VERSION,
    packages=['marionettejs'],
    install_requires=['django-compressor'],
    include_package_data=True,
    license='BSD License',  # example license
    description='A simple Django app to be extends for easier backbone development, it provides a base template to inherit',
    long_description=README,
    author='Tim Hsu',
    author_email='tim.yellow@gmail.com',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License', # example license
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ],
)
