from setuptools import setup, find_packages
import os

version = '1.0'

setup(name='wildcard.tinymceplugins.youtube',
      version=version,
      description="",
      long_description='%s\n%s' % (
          open("README.txt").read(),
          open(os.path.join("docs", "HISTORY.txt")).read()),
      classifiers=[
          "Framework :: Plone",
          "Programming Language :: Python",
          "Framework :: Plone :: 4.3"
      ],
      keywords='tinymce youtube plone',
      author='Nathan Van Gheem',
      author_email='nathan@vangheem.us',
      url='https://github.com/collective/wildcard.tinymceplugins.youtube',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['wildcard', 'wildcard.tinymceplugins'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'Products.TinyMCE'
      ],
      entry_points="""
      # -*- Entry points: -*-

      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
