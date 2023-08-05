import os
from setuptools import setup, find_packages

f = open(os.path.join(os.path.dirname(__file__), 'README.rst'))
README = f.read()
f.close()

setup(
    name='django-requestrepeat',
    version='0.5',
    packages=find_packages(),
    include_package_data=True,
    license='BSD License',  # example license
    description='A django app that repeats one http POST into several.',
    url='https://github.com/clickyspinny/django-requestrepeat/tree/master/requestrepeat',
    author='Oceana Technologies',
    author_email='ben@oceanatech.com',
    install_requires = [
    "Django>=1.1.1",
    "requests==2.5.1",
    ],
    long_description=README,
)