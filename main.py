# main.py
"""
Creates the app and defines its routes.
"""
import collections
import webapp2
import lib.handlers

handlers = [
    (r'/', handlers.MainHandler),
    (r'/login', handlers.LoginHandler),
    (r'/do-login', handlers.DoLoginHandler),
    (r'/register', handlers.RegisterHandler),
    (r'/do-register', handlers.DoRegisterHandler),
    (r'/signout', handlers.SignoutHandler),
    (r'/create-blog', handlers.CreateBlogHandler),
    (r'/blog-form', handlers.BlogFormHandler),
    (r'/blog/(\S+)', handlers.ViewBlogHandler),
    (r'/create-comment/(\S+)', handlers.CreateCommentHandler),
    (r'/edit-comment', handlers.EditCommentHandler),
    (r'/delete-comment', handlers.DeleteCommentHandler),
    (r'/like/(\S+)', handlers.LikeBlogHandler),
    (r'/edit-blog/(\S+)', handlers.EditBlogHandler),
    (r'/save-blog/(\S+)', handlers.SaveBlogHandler),
    (r'/delete-blog/(\S+)', handlers.DeleteBlogHandler)
]
app = webapp2.WSGIApplication(handlers, debug=True)
app.registry['template_eng'] = handlers.create_template_engine('templates')
app.registry['deleted_blogs'] = collections.deque()
