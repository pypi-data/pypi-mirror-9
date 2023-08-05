from setuptools import setup, find_packages
import os

version = '1.1.2'

setup(name='collective.interfaces',
      version=version,
      description="Adds interfaces tab to Plone's content where Manager's can manage marker interfaces.",
      long_description=open(os.path.join("collective", "interfaces", "README.txt")).read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from
      # http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        ],
      keywords='plone interface ui',
      author='Lukas Zdych',
      author_email='lukas.zdych@gmail.com',
      url='http://github.com/collective/collective.interfaces',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'Plone',
      ],
      entry_points="""
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
