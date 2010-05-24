#!/usr/bin/env python
from google.appengine.ext import db
from user_sn import User
from Content import Content
import logging

class Request(db.Model):
    user = db.ReferenceProperty(reference_class=User)
    file = db.ReferenceProperty(reference_class=Content)
    made = db.DateTimeProperty(auto_now_add=True)
    last_routed = db.DateTimeProperty(auto_now=True)
class RequestCopy(db.Model):
    file = db.ReferenceProperty(reference_class=Content)
    req = db.ReferenceProperty(reference_class=Request)
    #this can hold a variety of values.
    # Can be a USER (for get_from_local_cache, get_from_ext_cache)
    # Can be a Team + dest_int=TYPE_LOCAL_FD for (get_from_someone_on_team_not_tl, get_from_tl)
    # Can be a Team + dest_int=TYPE_EXTERN_FD for get_from_any_ext_cache
    # Can be None + dest_int = TYPE_EXTERNAL_RING for get_from_really_far_away
    dest = db.ReferenceProperty(collection_name="special")
    dest_int = db.IntegerProperty()
    #The user that we e-mailed to make the run
    emailed_user=db.ReferenceProperty(reference_class=User)

def copies_that_can_fulfill(request):
    from cache import ContentCopy
    return ContentCopy.all().filter("content =",request.file).fetch(limit=1000)

    
def cost_of_content(content):
    from math import ceil
    return int(ceil(0.5*content.file_size / 1024/1024))
def reward_for_content(content):
    from math import ceil
    return int(ceil(content.file_size / 1024/1024))
    
def send_run_msg(user):
    from mail import send_mail
    from magic import BASE_URL
    body = """Hey there,
    
    The sneakernet needs you!  Your elite sneakery skills are required to transport top-secret government data from A to B.  You can accept this mission by clicking this link:
    
    %s
    
    This message will self-destruct.
    
    Thanks,
    
    The sneakernet""" % (BASE_URL + "run")
    send_mail(to=user.email,subject="TOP SECRET MISSION",msg=body)
    

def get_from_local_cache(request,allcopies):
    logging.info("Searching team cache...")
    from cache import TYPE_LOCAL_FD, is_cache_available_soon
    for copy in allcopies:
        if copy.where.type == TYPE_LOCAL_FD and  copy.where.permanent_location.team_responsible.key() == request.user.team.key() and is_cache_available_soon(copy.where):
            logging.info("Found copy in the local team cache!")
            if RequestCopy.all().filter("file =",request.file).filter("dest =",request.user).get()==None:
                logging.info("No RequestCopy currently exists; creating...")
                rc = RequestCopy(file = request.file,req=request,dest=request.user,emailed_user=request.user)
                rc.put()
                send_run_msg(rc.emailed_user)
            else:
                logging.info("RequestCopy already exists")
            return True
    return False
def get_from_ext_cache(request,allcopies):
    logging.info("Searching (our) external cache...")
    from cache import TYPE_EXTERN_FD, is_cache_available_soon
    for copy in allcopies:
        if copy.where.type==TYPE_EXTERN_FD and copy.where.permanent_location.team_responsible.key() == request.user.team.key() and is_cache_available_soon(copy.where):
            logging.info("Found copy in the external cache!")
            if RequestCopy.all().filter("file =",request.file).filter("dest =",request.user).get()==None:
                logging.info("No RequestCopy currently exists; creating...")
                rc = RequestCopy(file = request.file,req=request,dest=request.user,emailed_user=request.user)
                rc.put()
                send_run_msg(rc.emailed_user)
            else:
                logging.info("RequestCopy already exists")
            return True
    return False
def get_from_tl(request,allcopies):
    logging.info("Searching team leader...")
    from user_sn import all_team_leaders_for
    leaders = all_team_leaders_for(request.user.team)
    leader_copies = []
    from cache import TYPE_COMPUTER, is_cache_available_soon, TYPE_LOCAL_FD
    for copy in allcopies:
        if copy.where.last_touched.team.key() == request.user.team.key() and copy.where.type==TYPE_COMPUTER and is_cache_available_soon(copy.where) and copy.where.last_touched.team_leader_flag:
            logging.info("Found copy from team leader!")
            dest = request.user.team
            if RequestCopy.all().filter("file =",request.file).filter("dest =",dest).filter("dest_int =",TYPE_LOCAL_FD).get()==None:
                logging.info("No RequestCopy currently exists; creating...")
                rc = RequestCopy(file = request.file,req=request,dest=dest,dest_int = TYPE_LOCAL_FD,emailed_user=copy.where.last_touched)
                rc.put()
                send_run_msg(rc.emailed_user)
            else:
                logging.info("RequestCopy already exists.")
            return True
    return False

def get_from_any_ext_cache(request,allcopies):
    logging.info("Searching all external caches...")
    from cache import TYPE_EXTERN_FD, is_cache_available_soon
    for copy in allcopies:
        if copy.where.type==TYPE_EXTERN_FD and is_cache_available_soon(copy.where):
            logging.info("Found a copy on team %s's external cache %s" % (copy.where.permanent_location.team_responsible.name, copy.where.friendlyName))
            dest = request.user.team
            if RequestCopy.all().filter("file =",request.file).filter("dest =",dest).filter("dest_int =",TYPE_EXTERN_FD).get()==None:
                logging.info("No RequestCopy currently exists; creating...")
                #we need to get ahold of a team leader
                from user_sn import all_team_leaders_for
                leaders = all_team_leaders_for(request.user.team)
                from random import choice
                flag_leader = choice(leaders)
                rc = RequestCopy(file = request.file,req=request,dest=dest,dest_int = TYPE_EXTERN_FD,emailed_user=flag_leader)
                rc.put()
                send_run_msg(flag_leader)
            else:
                logging.info("RequestCopy already exists.")
            return True
    return False
            
def get_from_someone_on_team_not_tl(request,allcopies):
    from cache import TYPE_COMPUTER, CacheLocation, TYPE_LOCAL_FD, is_cache_available_soon
    for copy in allcopies:
        if copy.where.last_touched.team.key() ==request.user.team.key() and copy.where.type==TYPE_COMPUTER and is_cache_available_soon(copy.where):
            if copy.where.last_touched.team_leader_flag:
                logging.info("Team leader has a copy; ignoring this copy for now")
                continue
            logging.info("Found copy from another teammember!")
            dest = request.user.team
            if RequestCopy.all().filter("file =",request.file).filter("dest =",dest).filter("dest_int =",TYPE_LOCAL_FD).get()==None:
                logging.info("No RequestCopy currently exists; creating...")
                rc = RequestCopy(file = request.file,req=request,dest=dest,dest_int=TYPE_LOCAL_FD,emailed_user=copy.where.last_touched)
                rc.put()
                send_run_msg(rc.emailed_user)
            else:
                logging.info("RequestCopy already exists")
            return True
    return False

def get_from_really_far_away(request,allcopies):
    from cache import TYPE_COMPUTER, TYPE_EXTERNAL_RING, is_cache_available_soon
    for copy in allcopies:
        if copy.where.type==TYPE_COMPUTER and is_cache_available_soon(copy.where):
            logging.info("Found a copy really far away")
            if RequestCopy.all().filter("file =",request.file).filter("dest_int =",TYPE_EXTERNAL_RING).get()==None:
                logging.info("No RequestCopy currently exists; creating...")
                rc = RequestCopy(file = request.file,req=request,emailed_user=copy.where.last_touched,dest_int = TYPE_EXTERNAL_RING)
                rc.put()
                send_run_msg(rc.emailed_user)
            else:
                logging.info("RequestCopy already exists")
            return True
        
            
            
    
def get_from_local_storage(request,allcopies):
    from cache import TYPE_COMPUTER
    from sneakfiles import host_sneakfile
    #Maybe it's in the user's local storage?
    logging.info("Checking loopback...")
    from magic import BASE_URL
    for copy in allcopies:
        #logging.info(copy.where.person_responsible)
        if copy.where.last_touched.key()==request.user.key() and copy.where.type==TYPE_COMPUTER:
            logging.info("Found local copy!")
            from user_sn import user_in_good_standing
            if not user_in_good_standing(request.user):
                logging.info("User not in good standing, so won't decrypt the file.")
                return True #mumble mumble
            from mail import send_mail
            sneakfile = "DECRYPT\n%s\n%s\n%s\n" % (copy.where.friendlyName,copy.content.file_id,copy.content.file_secret)
            body = """Ta-da!  We've got that %s you requested.  That wasn't so bad, was it?
            Just open the .sneak file hosted at %s and watch your file decrypt like magic!
            
            Glad we could help,
            
            The sneakernet""" % (copy.content.Name, BASE_URL + host_sneakfile(sneakfile))
            send_mail(request.user.email,"I've got something for you!",body)
            #give the sharer some points
            request.file.SharedBy.points += reward_for_content(request.file)
            request.file.SharedBy.put()
            request.delete()
            
            
            return True
    return False

def give_up(request):
    from mail import send_mail, alert_admins
    cost = cost_of_content(request.file)
    request.user.points += cost
    request.user.put()
    body = """Dear John,
    I tried.  I really did.  But for some strange reason I can't seem to get you the copy of %s you requested.
    I know it sucks.  I hate being a tease.  I did my best to get it to you, honest.  It just wasn't meant to be.
    Rest assured I've got a team of database wizards descending from the clouds to diagnose what went wrong.  But in our hearts, both of us always knew something wasn't quite right.  Those long runs, always expecting each other, but being rewarded... Long-distance relationships never seem to work out.
    
    You're welcome to try requesting it again.  Maybe this is just a temporary error?  I've given up hope, though.  It's time for me to move on.
    
    I'm returning the points I borrowed from you.  I can't bear to look at them anymore.
    
    Years from now, you will look back on this moment, and know it was for the best.  I hope we can still be friends.
    
    Yours truly,
    
    The sneakernet""" % request.file.Name
    send_mail(to=request.user.email,subject="Sorry",msg=body)
    alert_admins("Can't deliver %s to %s" % (request.file.Name,request.user.name))

    
def try_to_route(request):

    if request==None:
        logging.info("Nothing to do")
        return
    
    logging.info("Routing request %s which delivers %s to %s" % (request.key(),request.file.Name,request.user.name))
    request.put() #updates last_routed
    copies = copies_that_can_fulfill(request)
    logging.info("There are %d copies of this file on the sneakernet" % len(copies))
    if get_from_local_storage(request,copies):
        pass
    elif get_from_local_cache(request,copies):
        pass
    elif get_from_someone_on_team_not_tl(request,copies):
        pass
    elif get_from_ext_cache(request,copies):
        pass
    elif get_from_tl(request,copies):
        pass
    elif get_from_any_ext_cache(request,copies):
        pass
    elif get_from_really_far_away(request,copies):
        pass
    else:
        give_up(request)
        request.delete()
    