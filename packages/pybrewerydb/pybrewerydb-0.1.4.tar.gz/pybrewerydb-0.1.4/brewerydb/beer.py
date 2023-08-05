from .brewery import Brewery

class Beer(object):
    resource_url = 'beer'
    
    def __init__(self, data):
        self.data = data

    def __unicode__(self):
        return self.name
        
    @property
    def name(self):
        """ Returns the name of the
        beer """
        return self.data.get('name', None)
    
    @property
    def id(self):
        """ Returns the ID of the beer """
        return self.data.get('id', None)
    
    @property
    def abv(self):
        """ Returns the Alocohol By Volume of the beer """
        return self.data.get('abv', None)
    
    @property
    def ibu(self):
        """ Returns the IBU of the beer """
        return self.data.get('ibu', None)
    
    @property
    def description(self):
        """ Returns the description of the beer """
        return self.data.get('description', None)
    
    @property
    def organic(self):
        """ Returns a boolean on if the beer is
        organic or not """
        if self.data['isOrganic'] == 'Y':
            return True
        return False
    
    @property
    def year(self):
        """ Return the year the beer was first produced """
        return self.data.get('year', None)
    
    @property
    def style(self):
        """ Returns the name of the style
        category that this beer belongs to."""
        style = self.data.get('style', None)
        if style:
            return style['category']['name']
        else:
            return None
    
    @property
    def label_image_large(self):
        """ Return the large size label """
        return self.data['labels']['large']
    
    @property
    def label_image_medium(self):
        """ Return the medium size image """
        return self.data['labels']['medium']
    
    @property
    def brewery_id(self):
        """ Returns the brewery ID of the beer """
        breweries = self.data.get('breweries', None)
        if breweries:
            return breweries[0]['id']
        else:
            return None
    
    @property
    def brewery(self):
        """ Returns the brewery object. """
        breweries = self.data.get('breweries', None)
        if breweries:
            return breweries[0]
        else:
            return None
    
    
class Beers(Beer):
    resource_url = 'beers'