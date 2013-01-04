from django.conf.urls import patterns, include, url
from django.conf.urls.defaults import *
from django.views.generic import TemplateView

from blog.feed import AtomPostFeed, RSSPostFeed
from blog.views import AboutView, DayArchivePostView, ListPostView
from blog.views import PostDetailView, MonthArchivePostView, YearArchivePostView
from blog.views import PageDetailView

urlpatterns = patterns('blog.views',

    url(r'^$',
        view=ListPostView.as_view(),
        name='blog_index'
    ),

    url(r'^post/page/(?P<page>\d)/$',
        view=ListPostView.as_view(),
        name='blog_page'
    ),

    url(r'^post/(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{1,2})/(?P<slug>[-\w]+)/$',
        view=PostDetailView.as_view(),
        name='blog_post_detail',
    ),
        
    url(r'^post/(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{1,2})/$',
        DayArchivePostView.as_view(),
        name='blog_archive_day'
    ),

    url(r'^post/(?P<year>\d{4})/(?P<month>\d{2})/$',
        MonthArchivePostView.as_view(),
        name='blog_archive_month'
    ),

    url(r'^post/(?P<year>\d{4})/$',
        YearArchivePostView.as_view(),
        name='blog_archive_year'
    ),

    url(r'^page/(?P<slug>[-\w]+)/$',
        view=PageDetailView.as_view(),
        name='blog_page_detail',
    ),    
    
    url(r'^post/feed/$', AtomPostFeed(), name='feed_url'),
    url(r'^post/feed/atom/$', AtomPostFeed()),
    url(r'^post/feed/rss/$', RSSPostFeed()),
)
