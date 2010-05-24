from google.appengine.ext import webapp
from google.appengine.ext.webapp import util

class MovieHandler(webapp.RequestHandler):

  def post(self):
    from user_sn import confirm
    u = confirm(self)
    
    from Content import Content, TYPE_MOVIE, set_file_id
    c = Content(SharedBy = u,Name = self.request.get("title"),Type = TYPE_MOVIE,Link = self.request.get("imdb"))
    set_file_id(c)
    c.put()
    self.response.out.write("/share/upload?key=%s" % c.file_id)
class BookHandler(webapp.RequestHandler):
    def post(self):
        from user_sn import confirm
        u = confirm(self)
        from Content import Content, TYPE_BOOK, set_file_id
        c = Content(SharedBy = u, Name = self.request.get("title"),Type=TYPE_BOOK,Link=self.request.get("amzn"))
        set_file_id(c)
        c.put()
        self.response.out.write("/share/upload?key=%s" % c.file_id)
    
class UploadHandler(webapp.RequestHandler):
    def get(self):
        self.response.headers["Content-Type"] = "application/binary"
        self.response.headers["Content-Disposition"] = 'attachment; filename="upload.sneak"'
        from sneakfiles import make_sneakfile
        self.response.out.write(make_sneakfile("UPLOAD\n%s\n" % self.request.get("key")))
        
class UploadCompleteHandler(webapp.RequestHandler):
    def post(self):
        from user_sn import confirm
        u = confirm(self)
        from Content import content_by_id
        c = content_by_id(self.request.get("id"))
        if c.SharedBy.key() != u.key():
            raise Exception("You did not share this content")
        if c.file_secret is not None:
            raise Exception("Already completed updating this content")
        c.file_secret =self.request.get("key")
        c.file_size = long(self.request.get("size"))
        c.put()
        self.response.out.write("OK")
        
        

def main():
  application = webapp.WSGIApplication([('/share/movie', MovieHandler),
                                        ('/share/upload',UploadHandler),
                                        ('/share/book',BookHandler),
                                        ('/share/uploadcomplete',UploadCompleteHandler)],
                                       debug=True)
  util.run_wsgi_app(application)


if __name__ == '__main__':
  main()
