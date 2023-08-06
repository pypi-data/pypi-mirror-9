from setuptools import setup, find_packages
import os

version = '1.0'

setup(name='collective.blobsync',
      version=version,
      description="Rsync wrapper for rotated backups",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from
      # http://pypi.python.org/pypi?:action=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        ],
      keywords='rsync',
      author='Steve McMahon',
      author_email='steve@dcn.org',
      url='http://svn.plone.org/svn/collective/',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
      ],
      entry_points={
        'console_scripts': [
            'blobsync = collective.blobsync.main:main',
        ]
    },
      )
