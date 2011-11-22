from setuptools import setup

setup(name = 'easyply',
      version = '1.0.2',
      description = 'Helper functions for PLY (Python Lex & Yacc)',
      url = 'https://github.com/MHordecki/easyply',
      author = 'Mike Hordecki',
      author_email = 'mike@hordecki.com',
      packages = ['easyply'],
      long_description = open('README.rst').read(),
      data_files = (('', ('README.rst',)), ),
      install_requires = ('ply',),
      )
