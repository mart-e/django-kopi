from django.contrib import admin
from django.contrib.comments.models import Comment
from comments.models import KopiComment

admin.site.register(Comment)
admin.site.register(KopiComment)