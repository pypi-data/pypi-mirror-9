PyBreweryDB
===========

This is a Python wrapper around the BreweryDB API.  It is a work in progress with
only a handful of endpoints implemented at this point.


Documentation
-------------

Read the full documentation http://pybrewerydb.readthedocs.org


Installation
------------
Use pip::

    pip install pybrewerydb

Python Package Index https://pypi.python.org/pypi/pybrewerydb

Get yourself an API key to use https://www.brewerydb.com/auth/signup/ref/apps


Basic Usage
-----------

Create a PyBreweryDB instance using your api key:

    >>> from brewerydb.brewerydb import BreweryDB
    >>> brew_api = BreweryDB(key)
    >>> beers = brew_api.search_beer('fat tire')

Contributing
------------

Clone the repo at http://github.com/dstegelman/pybrewerydb

Feel free to log issues in Github or, better yet, submit a Pull Request against the ``master`` branch.

Licensing
---------

PyBreweryDB is distributed under the MIT License.
    

### Authors

* Derek Stegelman

Heavily inspried and several linez of codez drawn from PyMarvel by @gpennington
