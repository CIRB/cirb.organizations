from setuptools import setup, find_packages
import os

version = '1.2.dev0'

setup(name='cirb.organizations',
      version=version,
      description="",
      long_description=open("README.rst").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from
      # http://pypi.python.org/pypi?:action=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        ],
      keywords='',
      author='',
      author_email='',
      url='http://svn.plone.org/svn/collective/',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['cirb'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'Products.LinguaPlone',
          'Pillow',
          'z3c.saconfig',
          'plone.app.z3cform',
          'collective.z3cform.wizard',
          'collective.shuttle',
          'five.grok',
          'plone.namedfile',
          'plone.formwidget.namedfile',
          'cx_Oracle',
      ],
      extras_require = {
          'test': [
              'plone.app.testing',
          ]
      },
      entry_points="""
      # -*- Entry points: -*-

      [z3c.autoinclude.plugin]
      target = plone
      """,
      #setup_requires=["PasteScript"],
      #paster_plugins=["ZopeSkel"],
      )
