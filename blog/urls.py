from django.conf.urls import patterns, include, url
from django.conf.urls.defaults import *

from blog.feed import LatestPostFeed
from blog.views import AboutView, DayArchivePostView, ListPostView
from blog.views import PostDetailView, MonthArchivePostView, YearArchivePostView

urlpatterns = patterns('blog.views',

    url(r'^$',
        view=ListPostView.as_view(),
        name='blog_index'
    ),

    url(r'^(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{1,2})/(?P<slug>[-\w]+)/$',
        view=PostDetailView.as_view(),
        name='blog_post_detail',
    ),
        
    url(r'^(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{1,2})/$',
        DayArchivePostView.as_view()
    ),

    url(r'^(?P<year>\d{4})/(?P<month>\d{2})/$',
        MonthArchivePostView.as_view()
    ),

    url(r'^(?P<year>\d{4})/$',
        YearArchivePostView.as_view()
    ),
    (r'^feed/$', LatestPostFeed()),

    url(r'^about/$',view=AboutView.as_view(), name='about_url'),
)