#!/usr/bin/env python
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util, template
import hashlib
from user_sn import SALT
import logging

class MovieHandler(webapp.RequestHandler):

  def get(self):
    import os
    path = os.path.join(os.path.dirname(__file__),'resetPW.html')
    self.response.out.write(template.render(path,{"USERNAME":self.request.get("user"),"RESETCODE":self.request.get("resetcode")}))
  def post(self):
    from user_sn import get_user_by_name
    u = get_user_by_name(self.request.get("user"))
    if str(u.reset_code)==self.request.get("resetcode"):
        u.passwordhash = hashlib.md5(self.request.get("password")+SALT).hexdigest()
        #logging.info(self.request.get("password"))
        u.put()
        from mail import send_mail
        send_mail(to=u.email,subject="Sneakernet password reset.",msg="Your sneakernet password has been reset.  Hopefully you were the one who did this...")
    else: raise Exception("Incorrect reset code")
    


def main():
  application = webapp.WSGIApplication([('/resetPW', MovieHandler)],
                                       debug=True)
  util.run_wsgi_app(application)


if __name__ == '__main__':
  main()
