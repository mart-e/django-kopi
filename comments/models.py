import datetime

from django.db import models
from django.conf import settings
from django.contrib.comments.models import Comment
from django.utils.timezone import utc

from markdown import markdown
import hashlib
import requests

DEFAULT_AVATAR_URL = "/static/default_avatar.png"

class KopiComment(Comment):
    AVATAR_SIZE = 48

    identifier = models.CharField(max_length=50)
    comment_html = models.TextField(editable=False, blank=True)
    session_id = models.TextField(editable=False, blank=True)

    def get_avatar_url(self):
        if self.user_url:
            javatar = getJavatar(self.user_url)
            if javatar:
                #print("Javatar {0}".format(javatar))
                return javatar
        if self.user_email:
            gravatar =  getGravatar(self.user_email)
            if gravatar:
                #print("gravatar {0}".format(gravatar))
    		return gravatar

        #print("default {0}".format(DEFAULT_AVATAR_URL))
        return DEFAULT_AVATAR_URL


    def still_editable(self):
        """Check if a comment is not too old to be edited"""
        max_date = self.submit_date + datetime.timedelta(minutes=getattr(settings, 'COMMENT_ALTERATION_TIME_LIMIT', 15))
        return max_date > datetime.datetime.utcnow().replace(tzinfo=utc)
            

    def save(self, force_insert=False, force_update=False):
        self.comment_html = markdown(self.comment, safe_mode=True)
        super(KopiComment, self).save(force_insert, force_update)


def getJavatar(url):
    javatar_url = "{0}/avatar.png".format(url)
    avatar = requests.get(javatar_url)
    if avatar.status_code == 200 and avatar.headers['content-type'][:6] == "image/":
        return javatar_url
    else:
        return False


def getGravatar(email):
    md5 = hashlib.md5(email).hexdigest()
    # on websites with SSL, use https://secure.gravatar instead
    gravatar_url = "http://www.gravatar.com/avatar/{0}?s={1}&d=404".format(md5,KopiComment.AVATAR_SIZE)
    avatar = requests.get(gravatar_url)
    if avatar.status_code == 200:
        return gravatar_url
    else:
        return False
