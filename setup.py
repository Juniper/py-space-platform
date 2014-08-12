from setuptools import setup, find_packages

setup(name='space-ez',
      version='0.0.2',
      author='Roshan Joyce',
      author_email='rjoyce@juniper.net',
      packages=find_packages(),
      package_data={'jnpr.space': ['descriptions/*.*', 'templates/*.*']},
      install_requires=['requests',
                        'lxml',
                        'PyYAML',
                        'pytest',
                        'jinja2']
      )