from django.db import models
from bambu_oembed.managers import *

class Resource(models.Model):
    """A cached oEmbed resource"""
    
    url = models.URLField(max_length = 255, db_index = True)
    """The resource URL"""
    
    width = models.PositiveIntegerField()
    """The width of the cached resource"""
    
    html = models.TextField()
    """The cached resource's HTML"""
    
    objects = ResourceManager()
    
    def __unicode__(self):
        return self.url
    
    class Meta:
        unique_together = ('url', 'width')
        db_table = 'oembed_resource'
