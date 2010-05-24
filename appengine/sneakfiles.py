#!/usr/bin/env python
SNEAK_HEADER="SNEAK10\n"
def make_sneakfile(msg):
    return SNEAK_HEADER + msg
from google.appengine.ext import db



class Hosted_Sneakfile(db.Model):
    contents = db.TextProperty(required=True)
    
def host_sneakfile(msg):
    h = Hosted_Sneakfile(contents=msg)
    h.put()
    return "getsneakfile?sneakfile=%s" % h.key()
    
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


class MainHandler(webapp.RequestHandler):

  def get(self):
    self.response.headers["Content-Type"] = "application/binary"
    self.response.headers["Content-Disposition"] = 'attachment; filename="openthis.sneak"'
    s = Hosted_Sneakfile.get(self.request.get("sneakfile"))
    self.response.out.write(make_sneakfile(s.contents))
    s.delete()
class RunSneakHandler(webapp.RequestHandler):
    def get(self):
        self.response.headers["Content-Type"] = "application/binary"
        self.response.headers["Content-Disposition"] = 'attachment; filename="openthis.sneak"'
        self.response.out.write(make_sneakfile("RUN"))

def main():
  application = webapp.WSGIApplication([('/getsneakfile', MainHandler),
                                        ('/runsneakfile',RunSneakHandler)],
                                       debug=True)
  util.run_wsgi_app(application)


if __name__ == '__main__':
  main()
