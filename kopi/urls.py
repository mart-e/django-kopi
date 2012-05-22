from django.conf.urls import patterns, include, url
from django.conf import settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
                       url(r'^kopi/', include(admin.site.urls)),
    				   url(r'^static/(.*)$', 'django.views.static.serve', { 'document_root': settings.MEDIA_ROOT }),
)

urlpatterns += patterns('',
                        url(r'^', include('blog.urls')),
                        )
