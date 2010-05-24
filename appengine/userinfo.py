#!/usr/bin/env python


from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from magic import get_magic
import logging

class MainHandler(webapp.RequestHandler):

  def post(self):
    from user_sn import is_user_allowed, get_user_by_name
    u = get_user_by_name(self.request.get("username"))
    if is_user_allowed(u,self.request.get("password")):
        self.response.out.write('SUCCESS\n')
        self.response.out.write(str(u.points) + "\n")
        if (u.team_leader_flag):
            self.response.out.write("TEAM_LEADER\n")
        else:
            self.response.out.write("NOT_TEAM_LEADER\n")
        magic_i = get_magic()
        if magic_i.freeleech:
            self.response.out.write("FREELEECH\n")
        else:
            self.response.out.write("NOT_FREELEECH\n")
    else:
        logging.info("Authentication error...")


def main():
  application = webapp.WSGIApplication([('/userinfo', MainHandler)],
                                       debug=True)
  util.run_wsgi_app(application)


if __name__ == '__main__':
  main()
