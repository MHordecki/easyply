from setuptools import setup

setup(name='easyply',
      version='1',
      description='Helper functions for PLY (Python Lex & Yacc)',
      author='Mike Hordecki',
      author_email='mike@hordecki.com',
      packages=['easyply'],
      long_description = open('README.rst').read(),
      install_requires=[
        "ply",
        ]
      )
