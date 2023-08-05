from setuptools import setup, find_packages
import os

version = '1.0a1'

setup(name='c2.splitter.twocharacters',
      version=version,
      description="This product is split word to two characters for Plone.",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from
      # http://pypi.python.org/pypi?:action=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        ],
      keywords='plone splitter',
      author='Manabu TERADA',
      author_email='terada@cmscom.jp',
      url='https://www.cmscom.jp',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['c2', 'c2.splitter'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-

      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
