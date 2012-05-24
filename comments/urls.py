from django.conf.urls.defaults import *
from django.contrib.comments.urls import urlpatterns


urlpatterns = patterns('comments.views',
    url(r'^(?P<object_id>\d+)/edit/$',
        view='comment_edit',
        name='comments-edit'),

    url(r'^(?P<object_id>\d+)/remove/$',
        view='comment_remove',
        name='comments-remove'),

    # let's overwrite django.contrib.comments
    url(r'^post/$',
    	view='custom_comment_post',
    	name='comments-post-comment'),

    url( r'^', include( 'django.contrib.comments.urls' ) ),
)
