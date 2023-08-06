from setuptools import setup, find_packages

version = '0.1.0'
long_description = 'TODO'

setup(name='xmsg',
      version=version,
      description="Port of fedmsg to OSX notifications",
      long_description=long_description,
      classifiers=[
          "Intended Audience :: Developers",
          "License :: OSI Approved :: GNU General Public License (GPL)",
          "Programming Language :: Python :: 2",
      ],
      keywords='',
      author='Mike Nolan',
      author_email='me@nolski.rocks',
      url='http://github.com/nolski/xmsg',
      license='GPLv3+',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          "fedmsg",
          "fedmsg_meta_fedora_infrastructure"
      ],
      tests_require=[],
      entry_points="""
      [console_scripts]
      """,
      )
