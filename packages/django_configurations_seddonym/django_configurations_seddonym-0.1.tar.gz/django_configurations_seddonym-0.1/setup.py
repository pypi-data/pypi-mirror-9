from distutils.core import setup
from setuptools import find_packages


setup(
    name='django_configurations_seddonym',
    version='0.1',
    url='http://github.com/seddonym/django-configurations-seddonym/',
    author='David Seddon',
    author_email='david@seddonym.me',
    description='A pack of helpful django-configurations settings for my projects.',
    packages=find_packages(),
    include_package_data=True,
)
