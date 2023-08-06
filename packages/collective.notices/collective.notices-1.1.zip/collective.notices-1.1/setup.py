from setuptools import setup, find_packages
import os

version = '1.1'

long_description = (
    open('README.txt').read()
    + '\n' +
    open('docs/CONTRIBUTORS.txt').read()
    + '\n' +
    open('docs/CHANGES.txt').read()
    + '\n')

setup(name='collective.notices',
      version=version,
      description="Adds Site-Wide Notification/Status Messages for Plone CMS",
      long_description=long_description,
      # Get more strings from
      # http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        ],
      keywords='plone notification notice messages status',
      author='SoftFormance',
      author_email='contact@softformance.com',
      url='https://github.com/softformance/collective.notices',
      license='gpl',
      packages=find_packages('src'),
      package_dir = {'': 'src'},
      namespace_packages=['collective'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'zope.catalog',
          'zc.catalog',
          'plone.principalsource',
          'plone.directives.form',
          'plone.app.textfield',
          'plone.formwidget.autocomplete',
          'plone.app.dexterity',
          'python-dateutil',
      ],
      entry_points="""
      [z3c.autoinclude.plugin]
      target = plone
      """,
      extras_require = {'test': ['plone.app.testing']}
      )
