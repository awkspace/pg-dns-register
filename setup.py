from setuptools import setup, find_packages

with open('requirements.txt') as requirements_file:
    requirements = requirements_file.readlines()

setup(name='pg-dns-register',
      author='awk',
      author_email='self@awk.space',
      license='MIT',
      url='https://github.com/awkspace/pg-dns-register',
      install_requires=requirements,
      packages=find_packages(),
      entry_points={
          'console_scripts': [
              'pg-dns-register = pg_dns_register.cli:main'
          ]
      })
