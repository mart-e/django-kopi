from django.conf.urls import patterns, include, url
from django.conf import settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

from blog.views import ListPostView
# from kopi.views import AboutView
from django.views.generic import TemplateView

urlpatterns = patterns('',
                       url(r'^kopi/', view=TemplateView.as_view(template_name="about.html"), name='about_kopi'),
)

if settings.DEBUG:
    urlpatterns += patterns('',
        url(r'^uploads/(?P<path>.*)$', 'django.views.static.serve', {
            'document_root': settings.MEDIA_ROOT,
        }),
   )

urlpatterns += patterns('',
    					url(r'^admin/', include('grappelli.urls')),
                        url(r'^admin/', include(admin.site.urls)),
                        url(r'^static/(.*)$', 'django.views.static.serve', { 'document_root': settings.MEDIA_ROOT }),
                        url(r'^', include('blog.urls')),
                        url(r'^comments/', include('comments.urls')),
                        url(r'^photos/', include('media.urls.photos')),
                        url(r'^videos/', include('media.urls.videos')),
                        )
