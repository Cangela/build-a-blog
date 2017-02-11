import webapp2
import os
import jinja2

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


class Entry(db.Model):
    title = db.StringProperty(required = True)
    entry = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)

class MainPage(Handler):
    def render_new(self, title="", entry="", error=""):
        entries = db.GqlQuery("SELECT * FROM Entry "
                            "ORDER BY created DESC "
                            "LIMIT 5")
                            
        self.render("new_post.html", title=title, entry=entry, error=error, entries=entries)

    def get(self):
        self.render_new()

    def post(self):
        title = self.request.get("title")
        entry = self.request.get("entry")

        if title and entry:
            p = Entry(title = title, entry = entry)
            p.put()

            self.redirect("/")

        else:
            error = "We need both a title and some content!"
            self.render_new(title, entry, error)


app = webapp2.WSGIApplication([
    ('/', MainPage)
], debug=True)
