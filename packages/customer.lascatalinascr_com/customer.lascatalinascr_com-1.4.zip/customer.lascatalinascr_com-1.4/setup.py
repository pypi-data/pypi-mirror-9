from setuptools import setup, find_packages


version = '1.4'

long_description = (
    open('README.md').read()
    + '\n' +
    'Contributors\n'
    '============\n'
    + '\n' +
    open('CONTRIBUTORS.txt').read()
    + '\n' +
    open('CHANGES.txt').read()
    + '\n')

setup(name='customer.lascatalinascr_com',
      version=version,
      description=("Custom Implementations of the propertyshelf MLS embedding "
                   "for lascatalinascr.com"),
      long_description=long_description,
      # Get more strings from
      classifiers=[
          "Environment :: Web Environment",
          "Operating System :: OS Independent",
          "Framework :: Zope2",
          "Framework :: Plone",
          "Framework :: Plone :: 4.2",
          "Framework :: Plone :: 4.3",
          "Programming Language :: Python",
          "Programming Language :: Python :: 2.6",
          "Programming Language :: Python :: 2.7",
          "Topic :: Software Development :: Libraries :: Python Modules",
      ],
      keywords='Plone LasCatalinas Propertyshelf',
      author='Propertyshelf, Inc.',
      author_email='development@propertyshelf.com',
      url='https://github.com/propertyshelf/customer.lascatalinascr_com',
      license='gpl',
      packages=find_packages('src'),
      package_dir={'': 'src'},
      namespace_packages=['customer'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
          'plone.app.dexterity [grok]',
          'plone.directives.form',
          'plone.mls.listing >= 0.9.11',
      ],
      extras_require={'test': ['plone.app.testing']},
      entry_points="""
      # -*- Entry points: -*-
        [z3c.autoinclude.plugin]
        target = plone
      """,
      )
