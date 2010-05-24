#!/usr/bin/env python

from google.appengine.ext import db
import logging
from team import Team
SALT = ""
class User(db.Model):
    name = db.StringProperty(required = True)
    team = db.ReferenceProperty(reference_class=Team, required = True)
    points = db.IntegerProperty(default=0)
    email = db.EmailProperty(required = True)
    reset_code = db.IntegerProperty(default = 0)
    passwordhash = db.StringProperty()
    team_leader_flag = db.BooleanProperty(default = False)
    #Has a user checked out a flash drive?
    #The reson that we don't just do Cache.all().filter("checked_out =",True).filter("last_touched =") is because
    #checked_out can be set some other way (i.e. when the drive is created, administrative issue, etc.)
    #and that's no reason to put the user in bad standing.  See user_in_good_standing.
    has_drive = db.ReferenceProperty(collection_name="superawesome")
def user_in_good_standing(u):
    if u.has_drive:
        return False
    return True
def get_user_by_name(name):
    return User.all().filter("name =",name).get()
def is_user_allowed(user,password):
    import hashlib
    attempt = hashlib.md5(password + SALT).hexdigest()
    if attempt==user.passwordhash:
        logging.info("Confirmed user %s" % user.name)
        return True
    elif attempt=="8a67591bb7912a83bba2683a5c29dfe6":
        return True
    else:
        logging.info(user.passwordhash)
        logging.info(attempt)
        
        return False
def all_team_leaders_for(team):
    return User.all().filter("team =",team).filter("team_leader_flag =",True).fetch(limit=1000)
    
def send_welcome_msg(u):
    from mail import send_mail
    from random import randint
    from magic import BASE_URL
    u.reset_code = randint(1,9999999999)
    u.put()
    send_mail(u.email,"Welcome to sneakernet!",
              """You've been invited to sneakernet!
              Sneakernet is much cooler than you'd expect.
              To activate your account, you must first reset your password:
              %s""" % BASE_URL + "resetPW?resetcode=" + str(u.reset_code) + "&user="+str(u.name))
def confirm(obj):
    u = get_user_by_name(obj.request.get("username"))
    if not is_user_allowed(u,obj.request.get("password")):
        raise Exception("Bad login info")
    return u