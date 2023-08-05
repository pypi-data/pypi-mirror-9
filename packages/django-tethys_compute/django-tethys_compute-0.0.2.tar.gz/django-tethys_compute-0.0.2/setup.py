import os
from setuptools import setup

with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='django-tethys_compute',
    version='0.0.2',
    packages=['tethys_compute', 'tethys_compute/migrations'],
    include_package_data=True,
    license='BSD 2-Clause License',  # example license
    description='A Django app for adding computing resources admin controls to Tethys .',
    long_description=README,
    url='https://github.com/CI-WATER/TethysCluster/wiki',
    author='Scott Christensen',
    author_email='sdc50@byu.net',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        # Replace these appropriately if you are stuck on Python 2.
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
    install_requires = ['TethysCluster', 'condorpy'],
)