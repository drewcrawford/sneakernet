#!/usr/bin/env python

#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#


from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
import logging

def print_cache_info(cache):
    from cache import is_cache_available_now, is_cache_available_soon
    if is_cache_available_now(cache):
        avail = "Available"
    elif is_cache_available_soon:
        avail = "Checked out"
    else:
        avail = "Unavailable (WTF?)"
    return cache.friendlyName + "|" + str(cache.space_left/1024/1024) + " MB|" + str(cache.last_seen) + "|" + cache.last_touched.name + "|" + avail
class MainHandler(webapp.RequestHandler):

  def get(self):
    #get the whole team's caches
    from cache import CacheLocation, Cache, TYPE_LOCAL_FD, TYPE_EXTERN_FD
    from team import get_team_for_team_leader
    from user_sn import confirm
    from cache import TYPE_LOCAL_FD
    u = confirm(self)
    team = get_team_for_team_leader(u)
    locations = CacheLocation.all().filter("team_responsible =",team).filter("type =",TYPE_LOCAL_FD).fetch(limit=1000)
    locations += CacheLocation.all().filter("team_responsible =",team).filter("type =",TYPE_EXTERN_FD).fetch(limit=1000)
    for location in locations:
        if location.type == TYPE_LOCAL_FD:
            r = "INTERN"
        elif location.type == TYPE_EXTERN_FD:
            r = "EXTERN"
        logging.info("Writing info for location %s" % location)
        self.response.out.write(r+";"+location.description+";")
        self.response.out.write("/cache/img?cache=%s" % location.key() + ";")
        self.response.out.write(location.key())
        self.response.out.write(";")
        caches = Cache.all().filter("permanent_location =",location)
        for cache in caches:
            self.response.out.write(print_cache_info(cache))
            self.response.out.write(",")
        self.response.out.write("\n")
            
            
            
  def post(self):
    from cache import CacheLocation, TYPE_LOCAL_FD, TYPE_EXTERN_FD
    from user_sn import confirm
    from team import get_team_for_team_leader
    u = confirm(self)
    team = get_team_for_team_leader(u)
    if self.request.get("cache-key")=="MAKENEW":
        cl = CacheLocation()
    else:
        cl = CacheLocation.get(self.request.get("cache-key"))
    cl.team_responsible = team
    cl.description = self.request.get("description")
    replace_image = self.request.get("image")
    if replace_image != "":
        cl.image = replace_image
    if self.request.get("cache-type")=="INTERN":
        cl.type=TYPE_LOCAL_FD
    elif self.request.get("cache-type")=="EXTERN":
        cl.type = TYPE_EXTERN_FD
    else:
        raise Exception("I don't know the type.")
        
        
    cl.put()
    self.response.out.write("OK")

class FormatHandler(webapp.RequestHandler):
    def post(self):
        from user_sn import confirm
        from team import get_team_for_team_leader
        from cache import TYPE_EXTERN_FD, TYPE_LOCAL_FD
        u = confirm(self)
        team = get_team_for_team_leader(u)
        from cache import Cache, CacheLocation
        type = self.request.get("type")
        if type=="INTERN":
            ctype = TYPE_LOCAL_FD
        elif type=="EXTERN":
            ctype = TYPE_EXTERN_FD
        where = CacheLocation.get(self.request.get("location"))
        
        c = Cache(friendlyName = self.request.get("name"),type=ctype,last_touched=u,space_left=long(self.request.get("freespace")),permanent_location=where,checked_out=True)
        c.put()
        self.response.out.write("OK")
class InviteHandler(webapp.RequestHandler):
    def post(self):
        from user_sn import confirm
        from team import get_team_for_team_leader
        u = confirm(self)
        team = get_team_for_team_leader(u)
        from team import invite_person
        invite_person(u,self.request.get("email"))
    def get(self):
        from user_sn import confirm
        from team import get_team_for_team_leader
        u = confirm(self)
        team = get_team_for_team_leader(u)
        self.response.out.write(str(team.invites))



def main():
  application = webapp.WSGIApplication([('/teamadmin/cacheinfo', MainHandler),
                                        ('/teamadmin/format',FormatHandler),
                                        ('/teamadmin/invite',InviteHandler)],
                                       debug=True)
  util.run_wsgi_app(application)


if __name__ == '__main__':
  main()
