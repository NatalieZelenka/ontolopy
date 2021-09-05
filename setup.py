from setuptools import setup, find_packages
from distutils.util import convert_path

long_description = open('README.md', 'r').read()

# get version:
ns = {}
ver_path = convert_path('ontolopy/version.py')
with open(ver_path) as ver_file:
    exec(ver_file.read(), ns)

setup(name='ontolopy',
      version=ns['__version__'],
      install_requires=[
            'pandas',
            'numpy',
            'validators',
      ],
      description='Ontolopy is a package for working with ontology (.obo) files from Python.',
      long_description_content_type='text/markdown',
      long_description=long_description,
      packages=find_packages(),
      url='https://github.com/NatalieThurlby/ontolopy',
      author='Natalie Thurlby',
      classifiers=[
            "Programming Language :: Python :: 3",
      ],
      python_requires='>=3.6',
      author_email='natalie.thurlby@bristol.ac.uk',
      license='MIT')
