from django.db import models
from django.contrib.comments.models import Comment

from markdown import markdown
import hashlib
import requests

class KopiComment(Comment):
    identifier = models.CharField(max_length=50)
    comment_html = models.TextField(editable=False, blank=True)

    def get_avatar_url(self):
    	gravatar =  getGravatar(self.user_email)
    	if gravatar:
    		return gravatar



    def save(self, force_insert=False, force_update=False):
		self.comment_html = markdown(self.comment, safe_mode=True)
		super(KopiComment, self).save(force_insert, force_update)


def getJavatar(url):
	avatar = requests.get("{0}/avatar.png".format(url))
	if avatar:
		return avatar
	else:
		return False


def getGravatar(email):
	md5 = hashlib.md5(email).hexdigest()
	avatar = requests.get("https://secure.gravatar.com/avatar/{0}".format(md5))
	if avatar:
		return avatar
	else:
		return False
