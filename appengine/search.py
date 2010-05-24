#!/usr/bin/env python



from google.appengine.ext import webapp
from google.appengine.ext.webapp import util

#import google.appengine.ext.search
from Content import Content
import logging
def print_results(results):
    ret = ""
    for result in results:
        if result.file_size is None:
            continue
        ret += result.Name + "~"
        ret += str(result.Type) + "~"
        ret += str(result.shared_date) + "~"
        ret += str(result.file_size) + "~"
        ret += str(result.key()) + "~"
        ret += str(result.Link) + "~"
        ret += "\n"
    ret = ret.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;').replace("'", '&#39;')
    logging.info(ret)
    return ret
    
class RecentHandler(webapp.RequestHandler):

  def get(self):
    results = Content.all().order("-shared_date").fetch(limit=25)
    self.response.out.write(print_results(results))
class SearchHandler(webapp.RequestHandler):
    def get(self):
        results = Content.all().search(self.request.get("query")).fetch(limit=6)
        self.response.out.write(print_results(results))

def main():
  application = webapp.WSGIApplication([('/search/recent', RecentHandler),
                                        ('/search/search',SearchHandler)],
                                       debug=True)
  util.run_wsgi_app(application)


if __name__ == '__main__':
  main()
