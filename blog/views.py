from django.conf import settings
from django.views.generic import dates, list
from django.views.generic import TemplateView, DetailView

from blog.models import *

class AboutView(TemplateView):
    template_name = "about_blog.html"


class PostDetailView(dates.DateDetailView):
    template_name = 'blog/post_detail.html'
    model = Post
    month_format = '%m'
    date_field = 'publish'
    context_object_name = 'current_post'
    # TODO fix queryset to avoid showing draft

class ListPostView(list.ListView):
    model = Post
    month_format = '%m'
    date_field = 'publish'
    paginate_by = getattr(settings,'BLOG_PAGESIZE', 10)

    def get_queryset(self):
        return Post.objects.filter(status=2)

class YearArchivePostView(dates.YearArchiveView):
    model = Post
    date_field = 'publish'

    def get_queryset(self):
        return Post.objects.filter(status=2)

class MonthArchivePostView(dates.MonthArchiveView):
    model = Post
    month_format = '%m'
    date_field = 'publish'
    context_object_name = 'post_list'

    def get_queryset(self):
        return Post.objects.filter(status=2)

class DayArchivePostView(dates.DayArchiveView):
    model = Post
    month_format = '%m'
    date_field = 'publish'
    context_object_name = 'post_list'

    def get_queryset(self):
        return Post.objects.filter(status=1)

class PageDetailView(DetailView):
    model = Page
