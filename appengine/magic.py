#!/usr/bin/env python

BASE_URL="http://localhost:8083/"

from google.appengine.ext import db
class Magic (db.Model):
    freeleech = db.BooleanProperty(default=True)
    
def get_magic():
    magic = Magic.all().get()
    #put any hacks here
    #fix for corrupt description
    """from cache import CacheLocation
    c = CacheLocation.get("agpzbmVhazNybmV0chQLEg1DYWNoZUxvY2F0aW9uGPAHDA")
    c.description = ""
    c.put()"""
    #end hacks
    if magic is None:
        magic = Magic()
        magic.put()
    return magic