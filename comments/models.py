from django.db import models
from django.contrib.comments.models import Comment

from markdown import markdown

class KopiComment(Comment):
    identifier = models.CharField(max_length=50)
    comment_html = models.TextField(editable=False, blank=True)

    def get_avatar_url(self):
    	return "https://secure.gravatar.com/avatar/0c49d7e5a294cb2ca762eaede426b7a4?s=32&d=identicon&r=R"

    def save(self, force_insert=False, force_update=False):
		self.comment_html = markdown(self.comment, safe_mode=True)
		super(KopiComment, self).save(force_insert, force_update)