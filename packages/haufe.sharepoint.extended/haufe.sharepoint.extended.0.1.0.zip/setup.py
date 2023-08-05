import os
from setuptools import setup, find_packages

version = '0.1.0'

setup(name='haufe.sharepoint.extended',
      version=version,
      description="Experimental Python-Sharepoint connector w/ CopyList sharepoint",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='Sharepoint',
      author='Andreas Jung',
      author_email='info@zopyx.com',
      url='http://pypi.python.org/pypi/haufe.sharepoint',
      license='ZPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['haufe'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'suds',
          'argparse',
          'python-ntlm',
      ],
      entry_points=dict(
          console_scripts=['sharepoint-inspector=haufe.sharepoint.cli:main'],
      ),
      )
