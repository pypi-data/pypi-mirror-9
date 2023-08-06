from setuptools import setup, find_packages
import os

version = '1.1'

setup(name='graphite.theme',
      version=version,
      description="Graphite Theme for Bika LIMS",
      long_description=open("README.md").read() + "\n\n" +
                       open("docs/CHANGELOG.txt").read(),
      # Get more strings from
      # http://pypi.python.org/pypi?:action=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        ],
      keywords=['diazo', 'theme', 'lims', 'bika', 'opensource'],
      author='Naralabs',
      author_email='info@naralabs.com',
      url='http://github.com/naralabs/graphite.theme',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['graphite'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'bika.lims==3.1.7',
          'plone.app.theming',
      ],
      extras_require={
          'test': ['plone.app.testing',]
      },
      entry_points="""
      # -*- Entry points: -*-

      [z3c.autoinclude.plugin]
      target = plone
      """,
      #setup_requires=["PasteScript"],
      #paster_plugins=["ZopeSkel"],
      )
