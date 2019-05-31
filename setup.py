from setuptools import setup
 
long_description = open('README.md').read()
 
setup(name='uberon-py', # name your package
      packages=['uberon-py'], # same name as above
      version='0.0a1', 
      description='`uberon-py` is a package for querying the Uberon ontology from python.',
      long_description=long_description,
      url='https://github.com/NatalieThurlby/uberon-py',
      author='Natlie Thurlby',
      author_email='natalie.thurlby@bristol.ac.uk',
      license='GPLv3') # choose the appropriate license