# models.py
"""
Contains definitions for the following database object models:
- Account
- Blog
- BlogComment
"""

from datetime import datetime
from datetime import timedelta

from google.appengine.ext import ndb

def check_str_not_empty(prop, content):
    """Returns a datastore_errors.BadValueError if the string value of a Text
    or String property is empty.

    :param prop
        The ndb property type.
    :content
        The blog content.
    """
    if not content.strip():
        raise datastore_errors.BadValueError
    return content


class Account(ndb.Model):
    """
    Represents a user with an account to write blogs.

    Fields:
        id: The user name for the account.
        salt: The salt for the password for login cookies.
        psswdhash: The hash of the salt and the password.
    """
    salt = ndb.StringProperty(required=True)
    pwd_hash = ndb.StringProperty(required=True)


class Blog(ndb.Model):
    """
    Represents a blog entry.

    Fields:
        user: The blog author.
        title: The blog title.
        date: The date-time the blog was created.
        blog: The blog content.
        likes: The number of like votes.
    """
    user = ndb.StringProperty(required=True)
    title = ndb.StringProperty(required=True)
    date = ndb.DateTimeProperty(required=True, auto_now_add=True)
    text = ndb.TextProperty(required=True, validator=check_str_not_empty)
    likes = ndb.KeyProperty(kind=Account, repeated=True)

    def is_author(self, author):
        """Returns true if author is the author of this blog.

            Args:
                author: A user name.
        """
        return self.user == author

    @property
    def lines(self):
        """Splits the blog text into lines.

        :return
            A list of strings.
        """
        return self.text.split('\n')

    @property
    def tease(self):
        """Computes the tease of the blog."""
        MIN_TOKENS_IN_TEASE = 200
        MAX_TOKENS_IN_TEASE = 350
        if len(self.text) < MIN_TOKENS_IN_TEASE:
            return self.text
        index = MIN_TOKENS_IN_TEASE - 1
        space_index = 0
        found_dot = False
        # Try to parse full words, but not more than contain
        # MAX_TOKENS_IN_TEASE.
        while index < len(self.text) and index < MAX_TOKENS_IN_TEASE:
            c = self.text[index]
            if c.isspace():
                space_index = index
            if c == '.':
                found_dot = True
                break
            index += 1
        if found_dot:
            return self.text[:index]
        if space_index:
            return self.text[:space_index].rstrip()
        if MAX_TOKENS_IN_TEASE > len(self.text):
            return self.text
        return self.text[:MAX_TOKENS_IN_TEASE].rstrip()


class BlogComment(ndb.Model):
    """
    A blog commment.

    Fields:
        blog: The key property of the blog for which this is a comment.
        user: The user who posted this comment.
        date: The date-time the comment was posted.
        comment: The comment.
    """
    blog = ndb.KeyProperty(required=True)
    user = ndb.StringProperty(required=True)
    date = ndb.DateTimeProperty(required=True, auto_now_add=True)
    comment = ndb.TextProperty(required=True, validator=check_str_not_empty)

    @property
    def lines(self):
        """Splits the blog text into lines.

        :return
            A list of strings.
        """
        return self.comment.split('\n')

    def is_author(self, author):
        """Returns true if the author is the author of this comment.

        :param author
            A user name.
        :returns
            True if author is the author of this blog comment.
        """
        return self.user == author

    def get_timedelta(self):
        """Returns a string representing the timedelta since the comment was
        creted.
        """
        if not self.date:
            raise ValueError("comment has not been created yet")
        delta = datetime.now() - self.date
        if delta.days:
            if delta.days >= 365:
                years = delta.days / 365
                if years > 1: return "%d years ago" % years
                return "1 year ago"
            elif delta.days > 30:
                months = delta.days / 30
                if months > 1: return "d% months ago" % months
                return "1 month ago"
            elif delta.days > 7:
                weeks = delta.days / 7
                if weeks > 1: return "%d weeks ago" % weeks
                return "1 week ago"
            elif delta.days > 1:
                return "%d days ago" % delta.days
            return "1 day ago"
        if delta.seconds > 3600:
            hours = delta.seconds / 3600
            if hours > 1: return "%d hours ago" % hours
            return "1 hour ago"
        elif delta.seconds > 60:
            minutes = delta.seconds / 60
            if minutes > 1: return "%d minutes ago" % minutes
            return "1 minute ago"
        elif delta.seconds == 1:
            return "1 second ago"
        return "%d seconds ago" % delta.seconds
