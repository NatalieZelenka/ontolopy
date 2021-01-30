from setuptools import setup
 
long_description = open('README.md').read()
 
setup(name='uberon_py',
      packages=['uberon_py'],
      version='0.1.0',
      description='`uberon_py` is a package for querying the Uberon ontology from python.',
      long_description_content_type='text/markdown',
      long_description=long_description,
      url='https://github.com/NatalieThurlby/uberon-py',
      author='Natlie Thurlby',
      author_email='natalie.thurlby@bristol.ac.uk',
      license='MIT')
