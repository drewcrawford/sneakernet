#!/usr/bin/env python

from google.appengine.ext import db
from user_sn import User
from google.appengine.ext.search import SearchableModel
TYPE_MOVIE = 0
TYPE_BOOK = 1
class Content(SearchableModel):
    Name = db.StringProperty(required = True)
    Type = db.IntegerProperty(required = True)
    Link = db.URLProperty()
    SharedBy = db.ReferenceProperty(reference_class = User, required = True)
    file_id = db.StringProperty()
    file_secret = db.StringProperty()
    file_size = db.IntegerProperty() #search.py checks this for None to determine if it should be shown or not
    shared_date = db.DateTimeProperty(auto_now_add=True)
    
def set_file_id(c):
    from random import choice
    chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890"
    c.file_id = ""
    for i in range(0,8):
        c.file_id += choice(chars)
    c.put()
def content_by_id(id):
    return Content.all().filter("file_id =",id).get()