from setuptools import setup, find_packages
import os

version = '1.0b2'

setup(name='wildcard.cloudflare',
      version=version,
      description="",
      long_description="%s\n%s" % (
          open("README.txt").read(),
          open(os.path.join("docs", "HISTORY.txt")).read()),
      # Get more strings from
      # http://pypi.python.org/pypi?:action=list_classifiers
      classifiers=[
          "Framework :: Plone",
          "Programming Language :: Python",
      ],
      keywords='plone caching purging cloudflare',
      author='Nathan Van Gheem',
      author_email='nathan@vangheem.us',
      url='http://svn.plone.org/svn/collective/',
      license='GPL version 2',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['wildcard'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'plone.app.caching'
      ],
      extras_require={
          'test': ['plone.app.testing']
      },
      entry_points="""
      # -*- Entry points: -*-

      [z3c.autoinclude.plugin]
      target = plone
      """
      )
