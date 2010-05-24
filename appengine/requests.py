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
from user_sn import confirm
from request import Request, cost_of_content, try_to_route
from Content import Content
import logging



class MainHandler(webapp.RequestHandler):

  def post(self):
    user = confirm(self)
    content = Content.get(self.request.get("content"))
    #calculate points
    from math import ceil
    cost = cost_of_content(content)
    logging.info("cost %d" % cost)
    from magic import get_magic
    magic_mod = get_magic()
    if user.points >= cost or magic_mod.freeleech:
        r = Request(user=user,file=content)
        r.put()
        if not magic_mod.freeleech:
            user.points -= int(cost)
            user.put()
        self.response.out.write("OK")
    else:
        self.response.out.write("NEEDMOREPOINTS %d" % (cost - user.points))

class RouteHandler(webapp.RequestHandler):
    def get(self):
        req = Request.all().order("last_routed").get()
        try_to_route(req)
        


def main():
  application = webapp.WSGIApplication([('/requests', MainHandler),
                                        ('/requests/route',RouteHandler)],
                                       debug=True)
  util.run_wsgi_app(application)


if __name__ == '__main__':
  main()
