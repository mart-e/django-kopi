from django.db import models
from django.contrib.comments.models import Comment

class KopiComment(Comment):
    title = models.CharField(max_length=300)

    def get_avatar_url(self):
    	return "https://secure.gravatar.com/avatar/0c49d7e5a294cb2ca762eaede426b7a4?s=32&d=identicon&r=R"