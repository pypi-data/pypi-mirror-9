from setuptools import setup, find_packages

version = '0.1.4'

setup(name='pybrewerydb',
      version=version,
      description="Python wrapper for the BreweryDB API",
      long_description=open("README.md", "r").read(),
      classifiers=[
          "Development Status :: 1 - Planning",
          "Environment :: Console",
          "Intended Audience :: Developers",
          "Natural Language :: English",
          "Operating System :: OS Independent",
          "Programming Language :: Python",
          "Topic :: Internet :: WWW/HTTP :: Dynamic Content :: CGI Tools/Libraries",
          "Topic :: Utilities",
          "License :: OSI Approved :: MIT License",
          ],
      keywords='beer brewerydb api python',
      author='Derek Stegelman',
      author_email='dstegelman@gmail.com',
      url='http://github.com/dstegelman/PyBreweryDB',
      license='MIT',
      packages=find_packages(),
      install_requires=['requests'],
      include_package_data=True,
      zip_safe=True,
      )
