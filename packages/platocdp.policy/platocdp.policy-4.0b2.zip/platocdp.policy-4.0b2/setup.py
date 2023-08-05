from setuptools import setup, find_packages
import os

version = '4.0b2'

setup(name='platocdp.policy',
      version=version,
      description="",
      long_description=open("README.rst").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.rst")).read(),
      # Get more strings from
      # http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='',
      author='KOSLAB Technologies',
      author_email='izhar@kagesenshi.org',
      url='http://github.com/koslab/',
      license='gpl',
      packages=find_packages(),
      namespace_packages=['platocdp'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'z3c.unconfigure',
          'plone.app.dexterity [grok, relations]',
          'plone.namedfile [blobs]',
          'collective.grok',
          'plone.app.referenceablebehavior',
          'collective.dexteritytextindexer',
          'plone.app.multilingual',
          'plone.multilingualbehavior',
          'collective.documentviewer',
          'Solgema.fullcalendar',
          'eea.facetednavigation',
          'collective.unslider',
          'Products.ContentWellPortlets',
          'collective.plonetruegallery',
          'collective.ptg.fancybox',
          'collective.ptg.pikachoose',
          'collective.ptg.galleriffic',
          'collective.ptg.s3slider',
          'plone.app.multilingual',
          'plone.app.ldap',
          'collective.quickupload',
          'platocdp.newsportlet',
          'webcouturier.dropdownmenu',
          # -*- Extra requirements: -*-
      ],
      extras_require={
          'test': [
              'plone.app.testing',
           ],
      },
      entry_points="""
      # -*- Entry points: -*-
      [z3c.autoinclude.plugin]
      target = plone
      """,
      # The next two lines may be deleted after you no longer need
      # addcontent support from paster and before you distribute
      # your package.
      setup_requires=["PasteScript"],
      paster_plugins=["templer.localcommands"],

      )
