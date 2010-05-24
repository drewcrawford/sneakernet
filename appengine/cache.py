#!/usr/bin/env python

from google.appengine.ext import db
from google.appengine.ext import search
TYPE_LOCAL_FD = 0
TYPE_EXTERN_FD = 1
TYPE_COMPUTER = 2
TYPE_EXTERNAL_RING = 3 #not actually a cache type, but we use it as a destination flag
# to indicate it should be moved to any extern drive anywhere on the darknet if posssible
from user_sn import User
from Content import Content
from team import Team
class CacheLocation(db.Model):
    description = db.TextProperty()
    team_responsible = db.ReferenceProperty(reference_class=Team)
    image = db.BlobProperty()
    #remember, this is stored in two places: here and in the Cache itself
    type = db.IntegerProperty()
   

    
class Cache(db.Model):
    friendlyName = db.StringProperty()
    type = db.IntegerProperty(required = True)
    last_seen = db.DateTimeProperty(auto_now = True)
    last_touched = db.ReferenceProperty(reference_class=User)
    space_left = db.IntegerProperty(required=True)
    #person_responsible = db.ReferenceProperty(reference_class=User,collection_name="special")
    permanent_location = db.ReferenceProperty(reference_class=CacheLocation)
    #short-term checkout only
    checked_out = db.BooleanProperty(default=False)
    
    #Administratively set for long-term problems (like maybe a cache grew legs and walked away...)
    route_around_me = db.BooleanProperty(default=False)
    
    
class ContentCopy(db.Model):
    content = db.ReferenceProperty(reference_class=Content)
    where = db.ReferenceProperty(reference_class=Cache)

def can_operate_on(cache,user):
    #is it your cache?
    if cache.type==TYPE_COMPUTER and cache.last_touched.key()==user.key():
        return True
    #is it your team's local or ext  cache?
    elif  cache.type == TYPE_LOCAL_FD or cache.type==TYPE_EXTERN_FD and cache.permanent_location.team_responsible.key() == user.team.key() :
        return True
    elif cache.type ==TYPE_EXTERN_FD and user.team_leader_flag:
        return True
    return False
def get_cache_by_name(cache):
    return Cache.all().filter("friendlyName =",cache).get()

def get_copy(cacheid,fileid):
    from Content import content_by_id
    c = get_cache_by_name(cacheid)
    content = content_by_id(fileid)
    return ContentCopy.all().filter("content =",content).filter("where =",c).get()
def is_cache_available_soon(cache):
    import datetime
    diff = datetime.timedelta(days=15)
    if cache.last_seen + diff < datetime.datetime.today():
        return False
    if cache.route_around_me:
        return False
    return True
def is_cache_available_now(cache):
    if is_cache_available_soon(cache):
        if not cache.checked_out:
            return True
    return False
    
    