# -*- encoding: utf-8 -*-
from setuptools import setup, find_packages

install_requires = [
    'python-dateutil',
    'sphinx_rtd_theme',
    'pytest',
]

if __name__ == '__main__':
    setup(name='formskit',
          version='0.5.4.3',
          author=['Dominik "Socek" Długajczy'],
          url='https://github.com/socek/formskit/',
          description='Simple forms validation.',
          author_email=['msocek@gmail.com', ],
          packages=find_packages(),
          test_suite='formskit.tests.get_all_test_suite',
          )
