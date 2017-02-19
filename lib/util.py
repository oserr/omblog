import hmac
import random
import re
import string

from models import Account

def process_username(username):
    """Converts the username to lowercase, and returns a MatchObject if the
    username is valid.

    The username must begin with an alpha character, must be at least 4
    characters long, and it may only contain alphanumeric characters, dots, and
    underscores.

    :param username
        The username to validate.
    :return
        None or the match group.
    """
    username = username.strip().lower()
    m = re.match(r'[a-z][a-z\d._]{3,35}$', username)
    if m: return m.group()
    return None


def process_password(password):
    """Returns true if the password is valid, false otherwise.

    The password is valid if it contains between 6 and 35 characters, at least
    one number, at least one alpha character, and no whitespace.

    :param password
        The password to validate.
    """
    m = re.match(r'\S{6,35}$', password)
    if not m: return False
    for c in password:
        if c in string.ascii_letters: break
    else:
        return False
    for c in password:
        if c in string.digits: return True
    return False


def gensalt(length=16):
    """Generate a random salt value for a password.

    :param length
        The lenght of the salt value, with default value of 16.
    :return
        A string containing a randomly generated salt value composed of
        alphanumeric characters.
    """
    if not length or length < 0:
        raise ValueError('The salt length must be a positive integer')
    alnum = string.ascii_letters + string.digits
    return ''.join(random.choice(alnum) for _ in range(length))


def get_hash(salt, psswd):
    """Create a hash from a salt and password.

    :param salt
        The salt value. Cannot be empty.
    :param psswd
        The password value. Cannot be empty.
    :return
        A hash value of the salt and password.
    """
    if not salt or not psswd:
        raise ValueError('The salt and password cannot be empty')
    return hmac.new(salt.encode(), psswd).hexdigest()


def squeeze(letters, chars):
    """Replace each input sequence of a set of repeated characters with a single
    occurence of each respective character.

    :param letters
        A sequence of letters
    :param chars
        The set of characters to squeeze
    :return
        A new string with repeated characters removed.
    """
    if not letters:
        return ''
    if not chars:
        return letters
    seq = [None]
    for letter in letters:
        if letter not in chars or letter != seq[-1]:
            seq += letter
    return ''.join(seq[1:])
