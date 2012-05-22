from django.conf.urls import patterns, include, url
from django.conf.urls.defaults import *

from blog.views import AboutView, PostDetailView, DayArchivePostView, MonthArchivePostView, YearArchivePostView

urlpatterns = patterns('blog.views',

    url(r'^$', view=AboutView.as_view(), name='about_home'),
    url(r'^about/$',view=AboutView.as_view(), name='about_url'),

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
)