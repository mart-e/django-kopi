from django.conf.urls import patterns, include, url
from django.conf.urls.defaults import *

from wordpress.views import RedirectUploadsView

urlpatterns = patterns('',
                        # NOPE, doesn't work, need to sort with type
                        url(r'^wp-content/uploads/(?P<path>.*)$', RedirectUploadsView.as_view(), name="redirect-uploads"),
                        )
    
