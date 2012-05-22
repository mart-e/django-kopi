from django.conf.urls import patterns, include, url
from django.conf import settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

# from kopi.views import AboutView
from django.views.generic import TemplateView

urlpatterns = patterns('',
                       url(r'^kopi/', view=TemplateView.as_view(template_name="about.html"), name='about_kopi'),
)

urlpatterns += patterns('',
                        url(r'^admin/', include(admin.site.urls)),
                        url(r'^static/(.*)$', 'django.views.static.serve', { 'document_root': settings.MEDIA_ROOT }),
                        url(r'^', include('blog.urls')),
                        url(r'^comments/', include('comments.urls')),
                        )
