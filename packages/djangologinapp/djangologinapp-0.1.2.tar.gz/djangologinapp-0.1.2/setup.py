import os
from setuptools import setup

with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='djangologinapp',
    version='0.1.2',
    packages=['djangologinapp'],
    include_package_data=True,
    license='BSD License',  # example license
    description='A simple Django app to login and also with mongoengine as User backend.',
    long_description=README,
    url='https://github.com/abdullatheef/djangologinapp',
    author='latheef',
    author_email='latheefvkpadi@gmail.com',
    install_requires=[
        "requests",
	"mongoengine"
    ],
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
    ],
)
