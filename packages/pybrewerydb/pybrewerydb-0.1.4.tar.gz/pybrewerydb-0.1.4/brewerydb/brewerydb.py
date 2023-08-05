# -*- coding: utf-8 -*-

__author__ = 'Derek Stegelman'

import json
import requests
import urllib

from .beer import Beer, Beers
from .brewery import Brewery, Breweries


BASE_URL = 'http://api.brewerydb.com/v2'


class BreweryDB(object):
    def __init__(self, api_key):
        self.api_key = api_key
        
    def _auth(self):
        return "key=%s" % self.api_key
        
    def _call(self, resource_url, params=None):
        url = "%s/%s" % (BASE_URL, resource_url)
        
        if params:
            url += "?%s&%s" % (params, self._auth())
        else:
            url += "?%s" % self._auth()
        
        return requests.get(url)
    
    def _params(self, params):
        """
        Takes dictionary of parameters and returns
        urlencoded string

        :param params: Dict of query params to encode
        :type params: dict
        
        :returns:  str -- URL encoded query parameters
        """
        return urllib.urlencode(params)
    
    def search_beer(self, beer_name):
        """ Search the BreweryDB for a beer.  Returns a
        list of Beer objects.
        
        get /beers/
        
        :param beer_name: Query of the beer to search for
        :type params: string
        
        :returns:  List of Beer objects
        
        """
        response = json.loads(self._call("search", self._params(params={'q': beer_name, 'withBreweries': 'Y', 'type': 'beer'})).text)
        beers = []
        for beer in response['data']:
            beers.append(Beers(beer))
        return beers
        
    def get_beer(self, id):
        """Fetches a single beer by id.

        get /beer/<id>/

        :param id: ID of beer
        :type params: int
        
        :returns:  Beer object
        """        
        response = json.loads(self._call("%s/%s" % (Beer.resource_url, id), self._params({'withBreweries': 'Y'})).text)
        return Beer(response['data'])
        
    def search_breweries(self, brewery_name):
        """Fetches a single brewery by id.

        get /breweries/

        :param brewery_name: Search query for breweries
        :type params: string
        
        :returns:  List of brewery objects

        """
        response = json.loads(self._call('search', self._params(params={'q': brewery_name, 'type': 'brewery'})).text)
        breweries = []
        for brewery in response['data']:
            breweries.append(Brewery(brewery))
        return breweries
    
    def get_brewery(self, id):
        """Fetches a single character by id.

        get /brewery/<id>/

        :param id: ID of Brewery
        :type params: int
        
        :returns:  Brewery object
        """
        response = json.loads(self._call("%s/%s" % (Brewery.resource_url, id)).text)
        return Brewery(response['data'])