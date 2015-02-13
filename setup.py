from setuptools import setup, find_packages

setup(name='space-ez',
      version='0.0.2',
      author='Roshan Joyce',
      author_email='rjoyce@juniper.net',
      packages=find_packages(),
      package_data={'jnpr.space': ['descriptions/*.*',
                                   'descriptions/apps/servicenow/*.*',
                                   'descriptions/apps/serviceinsight/*.*',
                                   'templates/*.*']},
      install_requires=['requests>=2.5.1',
                        'lxml>=3.3.5',
                        'PyYAML>=3.11',
                        'pytest>=2.5.2',
                        'jinja2>=2.7.3']
      )
