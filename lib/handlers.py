# handlers.py
"""
Contains app logic.

The following handlers are defined:
- MainHandler
- LoginHandler
- DoLoginHandler
- RegisterHandler
- DoRegisterHandler
- SignoutHandler
- CreateBlogHandler
- BlogFormHandler
- ViewBlogHandler
- CreateCommentHandler
- EditCommentHandler
- DeleteCommentHandler
- LikeBlogHandler
- EditBlogHandler
- SaveBlogHandler
- DeleteBlogHandler
"""

import datetime
import os
import hmac
import json
import string

import jinja2
import webapp2
from google.appengine.ext import ndb

import util
import models

def create_template_engine(path=None):
    """Creats the template engine.

    :param path
        The path to the directory containing the templates for the application.
        Uses current working directory by default.
    :return
        A template environment.
    """
    if not path:
        path = os.getcwd()
    elif isinstance(path, str):
        if not os.listdir(path):
            raise ValueError('%s must exist and cannot be empty' % path)
    else:
        # Assume path is iterable. At least one directory is not empty.
        for directory in path:
            if os.listdir(directory):
                break;
        else:
            raise ValueError('path %s must contain at least one file' % path)
    loader = jinja2.FileSystemLoader(path)
    return jinja2.Environment(loader=loader)


class BaseHandler(webapp2.RequestHandler):
    """A wrapper to make request handlers less verbose to use."""

    def __init__(self, request, response):
        """Overrides initialization of request and response objects to get user
        name, and initializes session info with user name.

        :param request
            The request object
        :param response
            The response object
        """
        self.initialize(request, response)
        self.is_session = False
        self.user = None
        user = self.request.cookies.get('name')
        hsh = self.request.cookies.get('secret')
        if user and hsh:
            account = models.Account.get_by_id(user)
            if account and account.pwd_hash == hsh:
                self.user = user
                self.is_session = True

    def write(self, strval):
        """Wrapper around self.response.out.write.

        :param strval
            A string value.
        """
        return self.response.out.write(strval)

    def json_write(self, dictval):
        """Uses a dictionary to create a json response.

        :param dictval
            The dictionary used to create the json response.
        """
        return self.write(json.dumps(dictval))

    def json_read(self):
        """Reads the request body as a json object.

        :return
            A dictionary representing the json.
        """
        return json.loads(self.request.body)

    def render_str(self, context, template):
        """Uses a context and template to output string.

        The template engine must be defined in the app's registry.

        :param context
            A dictionary containing the context for the template.
        :param template
            The name of the file containing the template.
        """
        eng = self.app.registry.get('template_eng')
        if not eng:
            raise ValueError('template_eng must be defined in registry')
        template = eng.get_template(template)
        return template.render(context)

    def render(self, context, template):
        """Uses a context and template to render a page.

        The template engine must be defined in the app's registry.

        :param context
            A dictionary containing the context for the template.
        :param template
            The name of the file containing the template.
        """
        return self.write(self.render_str(context, template))


class MainHandler(BaseHandler):
    """Handle requests to the main blog site."""

    def get(self):
        """Render the main page with all the blogs."""
        context = {
            'blog_titles': self.get_blogs(),
            'loggedin': self.is_session
        }
        return self.render(context, 'content.html')

    def get_blogs(self):
        """Returns all blog entries in reverse chronological date, excluding
        blogs that have very recently been deleted but perhaps not reflected
        in this snapshot of blog entries.
        """
        blogs = models.Blog.query().order(-models.Blog.date).fetch()
        deleted_blogs = self.app.registry.get('deleted_blogs')
        while len(deleted_blogs):
            blog = deleted_blogs.pop()
            if blog in blogs:
                blogs.remove(blog)
        return blogs


class LoginHandler(BaseHandler):
    """Handle requests to login as a user of the blog site."""

    def get(self):
        """Render the login page."""
        # Should not be possible, because only people who are not logged in
        # should be able to see the link to sign in.
        if self.is_session:
            return self.redirect('/')
        context = {
            'action': 'sign in',
            'primary_action': 'do-login',
            'secondary_action': 'register',
            'message': "Don't have an account yet? Register..."
        }
        return self.render(context, 'signin.html')


class DoLoginHandler(BaseHandler):
    """Handle requests to login as a user of the blog site."""

    def post(self):
        """Verifies the user is registered.

        If the user is registered, then he is redirected to the main page,
        otherwise the user gets an error message indicating whether the
        username or password are incorrect.
        """
        # Should not be possible, because only people who are not logged in
        # should be able to see the link to sign in.
        if self.is_session:
            return self.redirect('/')

        data = self.json_read()
        data['success'] = False
        user = data['user']
        pwd = data['password']

        # verify account exists
        account = models.Account.get_by_id(user)
        if not account:
            data['baduser'] = True
            return self.json_write(data)

        # verify password is correct
        hsh = util.get_hash(account.salt, pwd)
        if hsh != account.pwd_hash:
            data['badpwd'] = True
            return self.json_write(data)

        # set session cookies
        data['success'] = True
        self.response.set_cookie('name', user)
        self.response.set_cookie('secret', hsh)
        return self.json_write(data)


class RegisterHandler(BaseHandler):
    """Handle requests to register as a user of the blog site."""

    def get(self):
        """Render the registration page."""
        # Should not be possible, because only people who are not logged in
        # should be able to see the link to sign in.
        if self.is_session:
            return self.redirect('/')
        context = {
            'action': 'register',
            'primary_action': 'do-register',
            'secondary_action': 'login',
            'message': "Have an account already? Sign in..."
        }
        return self.render(context, 'signin.html')


class DoRegisterHandler(BaseHandler):
    """Handle requests to register as a user of the blog site."""

    def post(self):
        """Registers a user.

        Checks the username and password are valid, and the username is not
        taken. If the username is taken, then the user is prompted for another
        username. The user is redirected to the main blog page after
        registration is complete.
        """
        # Should not be possible, because only people who are not logged in
        # should be able to see the link to sign in.
        if self.is_session:
            return self.redirect('/')

        data = self.json_read()
        user = data['user']
        pwd = data['password']

        # Check that username doesn't already exist
        account = models.Account.get_by_id(user)
        if account:
            data['success'] = False
            return self.json_write(data)

        # Create account
        salt = util.gensalt()
        hsh = util.get_hash(salt, pwd)
        account = models.Account(id=user, salt=salt, pwd_hash=hsh)
        try:
            account.put()
        except ndb.TransactionFailedError:
            data['success'] = False
            return self.json_write(data)

        data['success'] = True
        self.response.set_cookie('name', user)
        self.response.set_cookie('secret', hsh)
        return self.json_write(data)


class CreateCommentHandler(BaseHandler):
    """Handle requests to create a comment on a blog."""

    def post(self, urlkey):
        """Stores comment in the DB."""
        if not self.is_session:
            return self.redirect('/login')
        blog = ndb.Key(urlsafe=urlkey).get()
        if not blog:
            return self.error(404)
        text = self.json_read()['text']
        text = util.squeeze(text.strip(), string.whitespace)
        comment = models.BlogComment(blog=blog.key, user=self.user, comment=text)
        try:
            comment.put()
        except ndb.TransactionFailedError:
            # TODO: handle error as internal server error
            pass
        context = {'user': self.user, 'comment': comment}
        msg = self.render_str(context, 'comment.html')
        return self.json_write({'id': urlkey, 'comment': msg})


class SignoutHandler(BaseHandler):
    """Handle requests to signout."""

    def get(self):
        """Deletes session cookies and redirects to the main content page."""
        self.response.delete_cookie('name')
        self.response.delete_cookie('secret')
        return self.redirect('/')


class CreateBlogHandler(BaseHandler):
    """Handle requests to create a brand new blog entry."""

    def post(self):
        """Handles a post request to create a blog entry."""
        if not self.is_session:
            return self.redirect('/login')
        title = self.request.get('title').strip()
        title = util.squeeze(title, string.whitespace)
        text = self.request.get('text').strip()
        text = util.squeeze(text, string.whitespace)
        blog = models.Blog(user=self.user, title=title, text=text)
        try:
            blog.put()
        except ndb.TransactionFailedError:
            # TODO: Handle error
            return self.redirect('/')
        else:
            return self.redirect('/blog/%s' % blog.key.urlsafe())


class BlogFormHandler(BaseHandler):
    """Handles request initial request to create a blog entry."""

    def get(self):
        """Render the form to create a blog entry."""
        if not self.is_session:
            return self.redirect('/login')
        return self.render({'action': 'create-blog'}, 'blog-form.html')


class EditBlogHandler(BaseHandler):
    """Handles a request to edit a blog entry."""

    def get(self, urlkey):
        """Renders the form to edit a blog entry."""
        if not self.is_session:
            return self.redirect('/login')
        blog = ndb.Key(urlsafe=urlkey).get()
        if not blog:
            return self.error(404)
        context = {
            'action': 'save-blog',
            'entry_id': blog.key.urlsafe(),
            'title_value': blog.title,
            'text_value': blog.text
        }
        return self.render(context, 'blog-form.html')


class SaveBlogHandler(BaseHandler):
    """Handles a request to save a blog after an edit."""

    def post(self, urlkey):
        """Saves a blog after it is edited.

        :param urlkey
            The blog key in url safe format.
        """
        blog = ndb.Key(urlsafe=urlkey).get()
        blog.title = self.request.get('title').strip()
        blog.text = self.request.get('text').strip()
        # TODO: might be a good idea to add a last edited field to blog model
        try:
            blog.put()
        except ndb.TransactionFailedError:
            # TODO: handle error as internal server error
            pass
        finally:
            return self.redirect('/blog/%s' % urlkey)


class DeleteBlogHandler(BaseHandler):
    """Handles a request to delete a blog entry."""

    def get(self, urlkey):
        """Deletes a blog entry and redirects to the main page.

        :param urlkey
            The blog key in url safe format.
        """
        blog = ndb.Key(urlsafe=urlkey).get()
        query = models.BlogComment.query(models.BlogComment.blog == blog.key)
        comment_keys = [comment.key for comment in query.fetch()]
        try:
            blog.key.delete()
            ndb.delete_multi(comment_keys)
        except ndb.TransactionFailedError:
            # TODO: handle error as internal server error
            pass
        else:
            self.app.registry.get('deleted_blogs').append(blog)
        finally:
            return self.redirect('/')


class ViewBlogHandler(BaseHandler):
    """Handlers requests to view a blog entry."""

    def get(self, urlkey):
        """Renders a blog entry.

        :param urlkey
            The blog key in url safe format.
        """
        blog = ndb.Key(urlsafe=urlkey).get()
        q = models.BlogComment.query(models.BlogComment.blog == blog.key)
        comments = q.order(models.BlogComment.date).fetch()
        context = self.get_context(blog, self.is_session, comments)
        # check if user likes blog
        if self.is_session:
            context['user'] = self.user
            account = models.Account.get_by_id(self.user)
            if account.key in blog.likes:
                context['heart'] = 'red-heart'
        return self.render(context, 'blog.html')

    def get_context(self, blog, login_status, comments, user=None):
        """Creates the dictionary context for the template.

        :param blog
            The blog entry model.
        :param login_status
            Login status of user making request.
        :param comments
            List of blog comments.
        :return
            A dictionary with the context values for the template.
        """
        return {
            'blog': blog ,
            'loggedin': login_status,
            'blog_id': blog.key.urlsafe(),
            'comments': comments,
            'heart': 'normal',
            'user': user
        }


class EditCommentHandler(BaseHandler):
    """Handles the request to edit a blog comment."""

    def post(self):
        """Saves or deletes the comment and redirects to blog post."""
        data = self.json_read()
        comment = ndb.Key(urlsafe=data['id']).get()
        comment.comment = data['text'].strip()
        try:
            comment.put()
        except ndb.TransactionFailedError:
            # TODO: handle error as internal server error
            pass
        context = {'user': self.user, 'comment': comment}
        msg = self.render_str(context, 'comment.html')
        data = {'id': data['id'], 'comment': msg}
        return self.json_write(data)


class DeleteCommentHandler(BaseHandler):
    """Responds to a request to delete a comment in a blog."""

    def post(self):
        """Deletes a comment from the DB and responds to request."""
        data = self.json_read()
        comment_id = data['id']
        comment = ndb.Key(urlsafe=comment_id).get()
        data['id'] = None
        try:
            comment.key.delete()
            data['id'] = comment_id
        except ndb.TransactionFailedError:
            # TODO: handle error as internal server error
            pass
        return self.json_write(data)


class LikeBlogHandler(BaseHandler):
    """Responds to a request to like a blog entry."""

    def get(self, urlkey):
        """Adds like if user is logged in."""
        if not self.is_session:
            return self.redirect('/login')
        account = models.Account.get_by_id(self.user)
        blog = ndb.Key(urlsafe=urlkey).get()
        data = {'add': False, 'remove': False}
        # Don't allow users to like their own blogs
        if blog.is_author(self.user):
            return self.json_write(data)

        # User is unliking
        if account.key in blog.likes:
            blog.likes.remove(account.key)
            try:
                blog.put()
                data['remove'] = True
            except ndb.TransactionFailedError:
                # TODO: handle error as internal server error
                pass
            return self.json_write(data)

        # User is liking
        blog.likes.append(account.key)
        try:
            blog.put()
            data['add'] = True
        except ndb.TransactionFailedError:
            # TODO: handle error as internal server error
            pass
        return self.json_write(data)
