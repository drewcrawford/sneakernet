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

class SyncHandler(webapp.RequestHandler):

  def get(self):
    from cache import can_operate_on, ContentCopy, get_cache_by_name, Cache, TYPE_COMPUTER
    from user_sn import confirm
    u = confirm(self)
    cname = self.request.get("cache")
    logging.info("Syncing a cache named %s" % cname)
    c = get_cache_by_name(cname)
    if c==None:
        logging.info("No cached named %s, making a new one" % cname)
        c = Cache(friendlyName = cname,type=TYPE_COMPUTER,last_touched=u,space_left=-1,person_responsible=u)
        c.put()
    if not can_operate_on(c,u):
        raise Exception("You're not permitted to sync this cache.")
    #fetch everything that's "supposed" to be on the key
    copies = ContentCopy.all().filter("where =",c).fetch(limit=1000)
    self.response.out.write("OK\n")
    for copy in copies:
        self.response.out.write(copy.content.file_id + "\n")
  def post(self):
    from user_sn import confirm
    from cache import can_operate_on, get_copy, ContentCopy, get_cache_by_name, TYPE_COMPUTER, TYPE_EXTERN_FD, TYPE_LOCAL_FD, TYPE_EXTERNAL_RING
    from Content import content_by_id
    u = confirm(self)
    cname = self.request.get("cache")
    c = get_cache_by_name(cname)
    if not can_operate_on(c,u):
        raise Exception("You're not permitted to sync this cache.")
    deletes = self.request.get("deletes")
    for item in deletes.split("\n"):
        if item=="": continue
        logging.info("deleting %s" % item)
        get_copy(cname,item).delete()
    adds = self.request.get("adds")
    for item in adds.split("\n"):
        if item=="": continue
        logging.info("adding %s" % item)
        #see if there's an RC associated with this
        from request import RequestCopy
        content = content_by_id(item)
        rcs = RequestCopy.all().filter("file =",content)
        if c.type==TYPE_COMPUTER:
            rcs = rcs.filter("dest =",u).fetch(limit=1000)
        elif c.type==TYPE_LOCAL_FD:
            rcs = rcs.filter("dest =",c.permanent_location.team_responsible).filter("dest_int =",TYPE_LOCAL_FD).fetch(limit=1000)
        elif c.type==TYPE_EXTERN_FD:
            #the common case (closing the RC associated with a swap) is handled in runComplete.
            rcs = RequestCopy.all().filter("file =",content).filter("dest_int =",TYPE_EXTERNAL_RING).fetch(limit=1000)
        for rc in rcs:
            logging.info("Closing %s" % rc.key())
            rc.delete()
        co = ContentCopy(where = c,content=content)
        if co.content is None:
            logging.warning("Not adding %s" % item)
        else:
            co.put()
    c.space_left = int(self.request.get("size"))
    c.last_touched = u
    c.put()
    
    
class ImgHandler(webapp.RequestHandler):
    def get(self):
        from cache import CacheLocation
        c = CacheLocation.get(self.request.get("cache"))
        self.response.headers["Content-Type"] = "image/jpeg"
        self.response.out.write(c.image)
        #self.response.headers["Content-Disposition"] = 'attachment; filename="openthis.sneak"'

def main():
  application = webapp.WSGIApplication([('/cache/sync', SyncHandler),
                                        ('/cache/img',ImgHandler)],
                                       debug=True)
  util.run_wsgi_app(application)


if __name__ == '__main__':
  main()
