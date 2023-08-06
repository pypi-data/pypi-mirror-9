from setuptools import setup, find_packages

import os

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

version = '1.1.1'

long_description = \
    read('docs', 'README.rst') + '\n\n' + \
    read('CHANGES.txt')

setup(name='plone.app.contentlisting',
      version=version,
      description="Listing of content for the Plone CMS",
      long_description=long_description,
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        ],
      keywords='',
      author='Plone Foundation',
      author_email='plone-developers@lists.sourceforge.net',
      url='http://pypi.python.org/pypi/plone.app.contentlisting',
      license='GPL version 2',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['plone', 'plone.app'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'plone.uuid',
      ],
      extras_require={
        'test': [
            'plone.app.contenttypes',
            'plone.app.testing',
        ],
      },
      entry_points='''
      [z3c.autoinclude.plugin]
      target = plone
      ''',
      )
