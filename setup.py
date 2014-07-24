from setuptools import setup, find_packages

setup(name='space-ez',
      packages=find_packages(),
      install_requires=['requests',
                        'lxml',
                        'jinja2']
      )