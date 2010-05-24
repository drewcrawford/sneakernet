#!/usr/bin/env python
LEAVE_COPIES_ON_DARKNET = 3
LEAVE_COPIES_ON_TEAM = 1


PURGE_AT_WILL = 0
MOVE_TO_SOFTCACHE = 1
LEAVE_IN_PLACE=99
import logging

def team_of(contentcopy):
    from cache import TYPE_EXTERN_FD, TYPE_LOCAL_FD
    if contentcopy.where.type==TYPE_LOCAL_FD or contentcopy.where.type == TYPE_EXTERN_FD:
        return contentcopy.where.permanent_location.team_responsible
    else:
        return contentcopy.where.last_touched.team
def available_soon_cc(contentcopy):
    from cache import is_cache_available_soon
    return is_cache_available_soon(contentcopy.where)
def can_purge(user,contentcopy):
    from cache import ContentCopy, TYPE_COMPUTER
    allCopies = ContentCopy.all().filter("content =",contentcopy.content).fetch(limit = 1000) #now fetch all the copies
    allCopies = filter(available_soon_cc,allCopies) #only the ones that are online
    if len(allCopies) > LEAVE_COPIES_ON_DARKNET+1:
        copies_on_team = 0
        chk_team = team_of(contentcopy)
        for copy in allCopies:
            if copy.key()==contentcopy.key(): continue #not interested in the copy we want to purge
            if chk_team.key()==team_of(copy).key(): copies_on_team += 1
            if copies_on_team >= LEAVE_COPIES_ON_TEAM:
                if not user.team_leader_flag: #wait for the team leader to purge the crap.
                    team_leader_copies = filter(lambda x: x.where.type==TYPE_COMPUTER, copies_on_team)
                    from user_sn import all_team_leaders_for
                    leaders = all_team_leaders_for(user.team)
                    leaders = map(lambda x: x.key(),leaders)
                    team_leader_copies = filter(lambda x: x.where.last_touched.key() in leaders)
                    if len(team_leader_copies) != 0:
                        logging.info("Team leader has a copy.  Not purging.")
                        return MOVE_TO_SOFTCACHE
            else:            
                return PURGE_AT_WILL
    #this is conservative logic.  If there's an outstanding request on the sneakernet, leave the file in place
    from request import Request
    reqs = Request.all().filter("file =",contentcopy.content).get()
    if reqs==None:
        return MOVE_TO_SOFTCACHE
    return LEAVE_IN_PLACE


from google.appengine.ext import webapp
from google.appengine.ext.webapp import util


class MainHandler(webapp.RequestHandler):

  def get(self):
    from user_sn import confirm
    u = confirm(self)
    from cache import get_cache_by_name, can_operate_on, ContentCopy
    from Content import content_by_id
    
    c = get_cache_by_name(self.request.get("cache"))
    if not can_operate_on(c,u):
        raise Exception("You can't sync this cache.")
    content = content_by_id(self.request.get("content"))
    logging.info(c.key())
    logging.info(content.key())
    copy = ContentCopy.all().filter("where =",c).filter("content =",content).get()
    logging.info(copy)
    if copy is None:
        self.repsonse.out.write("NO_SUCH_THING")
        return
    result = can_purge(u,copy)
    if result==PURGE_AT_WILL:
        self.response.out.write("PURGE_AT_WILL")
        logging.info("PURGE_AT_WILL")
    elif result==MOVE_TO_SOFTCACHE:
        self.response.out.write("MOVE_TO_SOFTCACHE")
        logging.info("MOVE_TO_SOFTCACHE")
    else:
        self.response.out.write("LEAVE_IN_PLACE")
        logging.info("LEAVE_IN_PLACE")
    


def main():
  application = webapp.WSGIApplication([('/purge', MainHandler)],
                                       debug=True)
  util.run_wsgi_app(application)


if __name__ == '__main__':
  main()
