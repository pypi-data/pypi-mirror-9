from setuptools import setup, find_packages
import os

version = '1.0'

setup(name='cs.plonepatches.resourceregistries',
      version=version,
      description="A patch for Resource Registries to create a single minified file. Two if the user is logged-in",
      long_description=open("README.rst").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from
      # http://pypi.python.org/pypi?:action=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        ],
      keywords='',
      author='Mikel Larreategi & Lur Ibargutxi',
      author_email='mlarreategi@codesyntax.com',
      url='https://github.com/codesyntax/cs.plonepatches.resourceregistries',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['cs', 'cs.plonepatches'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'collective.monkeypatcher',
          'Plone>=4.2'
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-

      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
