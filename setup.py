from setuptools import setup

setup(name = 'easyply',
      version = '1.2',
      description = 'Helper functions for PLY (Python Lex & Yacc)',
      url = 'https://github.com/MHordecki/easyply',
      author = 'Mike Hordecki',
      author_email = 'mike@hordecki.com',
      packages = ['easyply'],
      long_description = open('README.rst').read(),
      install_requires = ('ply',),
      classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
      ]
      )
