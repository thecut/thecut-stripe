from setuptools import setup, find_packages
from version import get_git_version


setup(
    name='thecut-stripe',
    author='The Cut',
    author_email='development@thecut.net.au',
    url='https://projects.thecut.net.au/projects/thecut-stripe',
    namespace_packages=['thecut'],
    version=get_git_version(),
    packages=find_packages(),
    include_package_data=True,
    install_requires=['django-model-utils==2.2', 'oauth2client==1.3.1',
                      'stripe==1.19.1'],
)
