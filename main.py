import webapp2
import os
import jinja2
import re

from google.appengine.ext import db

# set up jinja
template_dir = os.path.join(os.path.dirname(__file__), "templates")
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                                autoescape = True)

class  Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))


class Blog(db.Model):
    title = db.StringProperty(required = True)
    blog_entry = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)

class MainPage(Handler):

    #def render_main(self, entries=""):
    def get(self, blog_entries=""):
        blog_entries = db.GqlQuery("SELECT * FROM Blog "
                        "ORDER BY created DESC "
                        "LIMIT 5")
        #t = jinja_env.get_template("mainpage.html")
        #content = t.render(
                        #entries = blog_entries
                        #)
        #self.response.write(content)

        self.render("mainpage.html", blog_entries=blog_entries)

class NewPost(Handler):
    def render_newpost(self, title="", blog_entry="", error=""):
        self.render("newpost.html", title=title, blog_entry=blog_entry, error=error)

    def get(self):
        self.render_newpost()

    def post(self):
        title = self.request.get("title")
        blog_entry = self.request.get("blog_entry")

        if title and blog_entry:
            b = Blog(title = title, blog_entry = blog_entry)
            b.put()
            self.redirect('/blog/%s' % str(b.key().id()))

        else:
            error = "We need both a title and some content!"
            self.render_newpost(title, blog_entry, error)

class ViewPostHandler(Handler):
    def get(self, id):

        blog_entry = Blog.get_by_id(int(id), parent=None)
        error =""
        if not blog_entry:
            error = "Incorrect blog id!"
        return self.render("singlepost.html", blog_entry=blog_entry, error=error)

app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/blog', MainPage),
    ('/newpost', NewPost),
    webapp2.Route('/blog/<id:\d+>', ViewPostHandler)
], debug=True)
