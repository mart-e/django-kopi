from django.views.generic import dates, list
from django.views.generic import TemplateView

from blog.models import *

class AboutView(TemplateView):
    template_name = "about_blog.html"


class PostDetailView(dates.DateDetailView):
    template_name = 'blog/post_detail.html'
    model = Post
    month_format = '%m'
    date_field = 'publish'
    context_object_name = 'current_post'

class ListPostView(list.ListView):
    model = Post
    month_format = '%m'
    date_field = 'publish'


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


