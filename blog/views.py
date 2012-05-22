from django.views.generic import dates
from django.views.generic import TemplateView

from blog.models import *

class AboutView(TemplateView):
    template_name = "about_blog.html"


class PostDetailView(dates.DateDetailView):
    model = Post
    month_format = '%m'
    date_field = 'publish'
    context_object_name = 'current_post'


class YearArchivePostView(dates.YearArchiveView):
    model = Post
    date_field = 'publish'

class MonthArchivePostView(dates.MonthArchiveView):
    model = Post
    month_format = '%m'
    date_field = 'publish'
    context_object_name = 'post_list'

class DayArchivePostView(dates.DayArchiveView):
    model = Post
    month_format = '%m'
    date_field = 'publish'
    context_object_name = 'post_list'


