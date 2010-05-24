from google.appengine.ext import webapp
from google.appengine.ext.webapp import util, template


class MovieHandler(webapp.RequestHandler):

  def get(self):
    import os
    path = os.path.join(os.path.dirname(__file__),'makenewteam.html')
    self.response.out.write(template.render(path,{}))
    
  def post(self):
    from user_sn import User, send_welcome_msg
    from team import Team
    import logging
    t = Team(name=self.request.get("teamname"))
    t.put()
    u = User(email=self.request.get("tlemail"),name=self.request.get("teamleader"),team=t,team_leader_flag=True)
    u.put()
    send_welcome_msg(u)
    

def main():
  application = webapp.WSGIApplication([('/makenewteam', MovieHandler)],
                                       debug=True)
  util.run_wsgi_app(application)


if __name__ == '__main__':
  main()
#!/usr/bin/env python

