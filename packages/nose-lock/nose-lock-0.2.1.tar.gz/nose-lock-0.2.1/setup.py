from setuptools import setup, find_packages

long_description = open('README.md').read()

try:
    # trying to convert long description from markdown to ReST
    # based on this article: https://coderwall.com/p/qawuyq

    import pypandoc
    long_description = pypandoc.convert('README.md', 'rst')
except ImportError, e:
    print 'NOPANDOC', e
    pass


setup(name='nose-lock',
      version='0.2.1',
      author='Alxander Artemenko',
      author_email='svetlyak.40wt@gmail.com',
      description=('A plugin for python-nose which locks test execution '
                   'and doesn\'t allow to run them in parallel '
                   'from two terminals.'),
      long_description=long_description,
      packages=find_packages(),
      setup_requires=['pypandoc'],
      install_requires=['lockfile>=0.10,<0.11'],
      entry_points = {
          'nose.plugins.0.10': [
              'lock = nose_lock:NoseLock'
          ]
      })
