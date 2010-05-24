#!/usr/bin/env python



from google.appengine.ext import webapp
from google.appengine.ext.webapp import util, template
import logging

def my_caches(u):
    from cache import Cache, TYPE_COMPUTER, is_cache_available_now
    return filter(is_cache_available_now,Cache.all().filter("last_touched =",u).filter("type =",TYPE_COMPUTER).fetch(limit=1000))
    
#returns team caches that are available NOW
def team_caches(u):
    from cache import CacheLocation, TYPE_LOCAL_FD, TYPE_EXTERN_FD, is_cache_available_now, Cache
    locs = CacheLocation.all().filter("team_responsible =",u.team).filter("type =",TYPE_LOCAL_FD).fetch(limit=1000)
    locs += CacheLocation.all().filter("team_responsible =",u.team).filter("type =",TYPE_EXTERN_FD).fetch(limit=1000)
    caches = []
    for loc in locs:
        caches += filter(is_cache_available_now,Cache.all().filter("permanent_location =",loc).fetch(limit=1000))
    return caches
    
def find_a_cache_to_get(u):
    #we should prioritize in terms of what gets things off the network the fastest
    from cache import TYPE_EXTERN_FD, TYPE_LOCAL_FD, TYPE_EXTERNAL_RING, is_cache_available_now, ContentCopy, Cache
    from request import RequestCopy
    teamcaches = team_caches(u)
    externs = filter(lambda x: x.type==TYPE_EXTERN_FD,teamcaches)
    if u.team_leader_flag:
        #try to do a team leader run
        rcs = RequestCopy.all().filter("dest =",u.team).filter("dest_int =",TYPE_EXTERN_FD).fetch(limit=1000)
        for rc in rcs:
            #figure out where to get that file
            #get all the external ring drives
            ringdrives = Cache.all().filter("type =",TYPE_EXTERN_FD)
            ringdrives = filter(is_cache_available_now,ringdrives)
            for drive in ringdrives:
                if drive.permanent_location.team_responsible.key()==u.team.key():
                    logging.error("Our own ext cache %s has a copy of %s.  I'm going to ignore this, but probably something bad is happening." % (drive.key(),rc.file.key()))
                    continue
                copy = ContentCopy.all().filter("content =",rc.file).filter("where =",drive).get()
                if copy is not None:
                    logging.info("We need to get ahold of drive %s" % drive.friendlyName)
                    
                    for swapdrive in externs:
                        if not is_cache_available_now(swapdrive): continue
                        logging.info("We will trade %s for it" % swapdrive.friendlyName)
                        return (drive,swapdrive)
                    logging.info("We don't have a drive we can swap for it :-()")
    
    
    #get off extern

    rcs = RequestCopy.all().filter("dest =",u).fetch(limit=1000) #find all requests headed for me


    

    for cache in externs:
        for rc in rcs:
            cc = ContentCopy.all().filter("where =",cache).filter("content =",rc.file).get()
            if cc is not None:
                logging.info("User needs a file from extern cache; instructing user to acquire it")
                return (cache,None)
    #put on extern
    mycaches = my_caches(u)
    for cache in mycaches:
        ccs = ContentCopy.all().filter("where =",cache)
        for cc in ccs:
            rc = RequestCopy.all().filter("file =",cc.content).filter("dest_int =",TYPE_EXTERNAL_RING).get()
            if rc is not None:
                logging.info(rc)
                logging.info("User needs to dump a file to external ring; filesize is %s" % (rc.file.file_size))
                for cache in externs:
                    if cache.space_left > rc.file.file_size:
                        return (cache,None)
                    logging.info("Can't find a cache that will hold that file :-(")
                    
    
    locs = filter(lambda x: x.type==TYPE_LOCAL_FD,teamcaches)
    for cache in locs:
        for rc in rcs:
            cc = ContentCopy.all().filter("where =",cache).filter("content =",rc.file).get()
            if cc is not None:
                logging.info("User needs a file from local team cache; instructing user to acquire it.")
                return (cache,None)

    #find any request we can actually fulfill
 
    for cache in mycaches:
        ccs = ContentCopy.all().filter("where =",cache)
        for cc in ccs:
            #any RC with a file we can access that is also bound for our team
            rc = RequestCopy.all().filter("file =",cc.content).filter("dest =",u.team).get()
            if rc is not None:
                #find a cache big enough to hold it
                logging.info(rc)
                logging.info("User needs to dump a file to a team cache; file is size %s" % (rc.file.file_size))
                for cache in locs:
                    if cache.space_left > rc.file.file_size:
                        return (cache,None)
                logging.info("Can't find a cache that will hold that file.  :-(")
    return (None,None)
                    
                
                
    
    
class MainHandler(webapp.RequestHandler):

  def get(self):
    import os
    path = os.path.join(os.path.dirname(__file__),'run.html')
    self.response.out.write(template.render(path,{}))
  def post(self):
    if self.request.get("accept1")!="on" or self.request.get("accept2")!="on":

        logging.info("Not accepted")
        self.get()
        return
    #find something to do
    from user_sn import confirm
    u = confirm(self)
    if u.has_drive is not None:
        logging.info("User has drive %s, run denied." % u.has_drive.key())
        self.response.out.write("You already have a drive checked out!  You must return it.  Contact the admin or your team leader.")
        return
    (cache,swap) = find_a_cache_to_get(u)
    import os
    if cache==None:
        self.response.out.write("Can't find anything to do.  Sorry...")
    elif swap==None:
        #mark the cache checked out
        cache.checked_out = True
        cache.last_touched = u
        cache.put()
        u.has_drive = cache
        u.put()
        data = {"CACHENAME":cache.friendlyName,
                "IMGURL":"/cache/img?cache="+str(cache.permanent_location.key()),
                "DESCRIPTION":cache.permanent_location.description,
                "USERNAME":self.request.get("username"),
                "PASSWORD":self.request.get("password")}
        path = os.path.join(os.path.dirname(__file__),'run_progress.html')
        self.response.out.write(template.render(path,data))
    else:
        #swap drive
        logging.info("User %s swapping drive %s and %s" % (u.name,cache.friendlyName,swap.friendlyName))
        cache.checked_out = True
        cache.last_touched = u
        cache.put()
        swap.checked_out = True
        swap.last_touched = u
        swap.put()
        u.has_drive = cache
        u.put()
        data = {"CACHENAME":cache.friendlyName,
                "SWAPNAME":swap.friendlyName,
                "DESCRIPTION":cache.permanent_location.description,
                "SWAPDESCRIPTION":swap.permanent_location.description,
                "SWAPURL":"/cache/img?cache="+str(swap.permanent_location.key()),
                "IMGURL":"/cache/img?cache="+str(cache.permanent_location.key()),
                "USERNAME":self.request.get("username"),
                "PASSWORD":self.request.get("password")}
        path = os.path.join(os.path.dirname(__file__),'run_swap.html')
        self.response.out.write(template.render(path,data))
        
        

class RunCompleteHandler(webapp.RequestHandler):
    def post(self):
        from user_sn import confirm
        from cache import Cache
        u = confirm(self)
        cache = u.has_drive
        u.has_drive.checked_out = False
        u.has_drive.put()
        u.has_drive = None
        u.put()
        logging.info("User %s returning cache %s" % (u.name,cache.friendlyName))
        self.response.out.write("Thanks!  Mission complete!")
class SwapCompleteHandler(webapp.RequestHandler):
    def post(self):
        from user_sn import confirm
        from cache import Cache, get_cache_by_name
        u = confirm(self)
        cache = get_cache_by_name(self.request.get("cachename"))
        swap = get_cache_by_name(self.request.get("swapname"))
        cache.checked_out = False
        temp = cache.permanent_location
        cache.permanent_location = swap.permanent_location
        cache.put()
        swap.permanent_location = temp
        swap.checked_out = False
        swap.put()
        u.has_drive = None
        u.put()
        logging.info("User %s completed swapping %s and %s" % (u.name,cache.friendlyName,swap.friendlyName))
        from request import RequestCopy
        self.fulfill(cache)
        self.fulfill(swap)
        
        self.response.out.write("Thanks!  Mission complete!")
    def fulfill(self,cache):
        from request import RequestCopy
        from cache import TYPE_EXTERN_FD, ContentCopy, get_copy
        fulfill_swap_requests = RequestCopy.all().filter("dest =",cache.permanent_location.team_responsible).filter("dest_int =",TYPE_EXTERN_FD).fetch(limit=1000)
        for request in fulfill_swap_requests:
            logging.info("thinking about request %s" % request.key())
            stuff_on_disk = ContentCopy.all().filter("content =",request.file).filter("where =",cache).get()
            if stuff_on_disk is not None:
                logging.info("Closing requestcopy %s" % request.key())
                request.delete()
            else:
                logging.info("stuff on disk is none")
            
    
                
class MoveToHandler(webapp.RequestHandler):
    def post(self):
        diskstr = self.request.get("disks")
        disks = []
        from request import RequestCopy
        for disk in diskstr.split("\n"):
            if disk=="": continue #ignore trailing \n
            disks.append(disk.strip())
        from user_sn import confirm
        from cache import Cache, TYPE_COMPUTER, TYPE_EXTERNAL_RING, TYPE_LOCAL_FD, TYPE_EXTERN_FD
        u = confirm(self)
        result = []
        for disk in disks:
            logging.info("Considering disk %s" % disk)
            real_disk = Cache.all().filter("friendlyName =",disk).get()
            if real_disk.type==TYPE_COMPUTER:
                wants_files = RequestCopy.all().filter("dest =",u).fetch(limit=1000)
                """The line below handles a really weird edge case:
                1.  Bob requests a file.  The file moves along however and ends up (for the moment) on the team_extern cache
                2.  The team leader syncs the cache as part of the run.  They should back up the file appropriately.
                3.  If somebody else syncs the cache first (for whatever reason) they'll back it up too"""
                wants_files += RequestCopy.all().filter("dest =",u.team).filter("dest_int =",TYPE_EXTERN_FD)
            elif real_disk.type==TYPE_LOCAL_FD:
                wants_files = RequestCopy.all().filter("dest =",real_disk.permanent_location.team_responsible).fetch(limit=1000)
            elif real_disk.type==TYPE_EXTERN_FD:
                wants_files = RequestCopy.all().filter("dest_int =",TYPE_EXTERNAL_RING)
            result.append((real_disk,wants_files))
    
        self.response.out.write("OK\n")
        for (disk,rcs) in result:
            self.response.out.write(disk.friendlyName)
            self.response.out.write(":")
            for rc in rcs:
                self.response.out.write(rc.file.file_id)
                self.response.out.write("|")
            self.response.out.write("\n")
        
class PurgeHandler(webapp.RequestHandler):
    def post(self):
        pass

            
                
        

def main():
  application = webapp.WSGIApplication([('/run', MainHandler),
                                        ('/run/MoveTo',MoveToHandler),
                                        ('/run/purge',PurgeHandler),
                                        ('/run/complete',RunCompleteHandler),
                                        ('/run/swapcomplete',SwapCompleteHandler)],
                                       debug=True)
  util.run_wsgi_app(application)


if __name__ == '__main__':
  main()
