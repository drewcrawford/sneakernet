#!/usr/bin/env python
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util, template
class MainHandler(webapp.RequestHandler):

  def get(self):
    import os
    path = os.path.join(os.path.dirname(__file__),'acceptInvite.html')
    self.response.out.write(template.render(path,{"INVITECODE":self.request.get("code")}))
  def post(self):
    from user_sn import User, send_welcome_msg
    from team import Invite
    username = self.request.get("username")
    if User.all().filter("name =",username).get() is not None:
        raise Exception("I already have that user...")
    invite = Invite.get(self.request.get("code"))
    if invite is None:
        raise Exception("Bad invite code!")
    u = User(name=username,team=invite.team,email=invite.email)
    u.put()
    send_welcome_msg(u)
    invite.delete()
    
        
    
def main():
  application = webapp.WSGIApplication([('/accept_invite', MainHandler)],
                                       debug=True)
  util.run_wsgi_app(application)


if __name__ == '__main__':
  main()
