from django.views.generic import dates
from django.views.generic import TemplateView

from blog.models import *

class PostDetailView(dates.DateDetailView):
    model = Post
    month_format = '%m'
    date_field = 'publish'
    template_object_name = 'current_post',

class AboutView(TemplateView):
    template_name = "about_blog.html"