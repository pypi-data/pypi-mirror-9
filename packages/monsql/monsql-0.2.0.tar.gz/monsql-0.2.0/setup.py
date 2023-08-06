from setuptools import setup, find_packages

setup(name='monsql',
      version='0.2.0',
      packages = find_packages(),
      author='firstprayer',
      author_email='zhangty10@gmail.com',
      description='MonSQL - Lightweight and use-friendly wrapper for multiple relational databases. Currently supporting MySQL, SQLite3, PostgreSQL',
      url='https://github.com/firstprayer/monsql.git',
      install_requires=[
      	'MySQL-python'
      ],
)
