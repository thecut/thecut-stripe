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
    install_requires=['django-jsonfield==0.9.13', 'django-model-utils==2.2',
                      'oauth2client==1.3.1', 'sphinx==1.2.3',
                      'stripe==1.19.1'],
)
