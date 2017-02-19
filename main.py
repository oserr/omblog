# main.py
"""
Creates the app and defines its routes.
"""
import collections
import webapp2
from lib import handlers as hdl

handlers = [
    (r'/', hdl.MainHandler),
    (r'/login', hdl.LoginHandler),
    (r'/do-login', hdl.DoLoginHandler),
    (r'/register', hdl.RegisterHandler),
    (r'/do-register', hdl.DoRegisterHandler),
    (r'/signout', hdl.SignoutHandler),
    (r'/create-blog', hdl.CreateBlogHandler),
    (r'/blog-form', hdl.BlogFormHandler),
    (r'/blog/(\S+)', hdl.ViewBlogHandler),
    (r'/create-comment/(\S+)', hdl.CreateCommentHandler),
    (r'/edit-comment', hdl.EditCommentHandler),
    (r'/delete-comment', hdl.DeleteCommentHandler),
    (r'/like/(\S+)', hdl.LikeBlogHandler),
    (r'/edit-blog/(\S+)', hdl.EditBlogHandler),
    (r'/save-blog/(\S+)', hdl.SaveBlogHandler),
    (r'/delete-blog/(\S+)', hdl.DeleteBlogHandler)
]
app = webapp2.WSGIApplication(handlers, debug=True)
app.registry['template_eng'] = hdl.create_template_engine('templates')
app.registry['deleted_blogs'] = collections.deque()
