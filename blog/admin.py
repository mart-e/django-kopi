from django.contrib import admin
from blog.models import *

def direct_url(obj):
    return u'<a href="%s">#</a>' % (obj.get_absolute_url())
direct_url.short_description = 'url'
direct_url.allow_tags = True

class PostAdmin(admin.ModelAdmin):
    list_display  = ('title', 'publish', 'status', direct_url)
    list_filter   = ('publish', 'status')
    search_fields = ('title', 'body')
    prepopulated_fields = {'slug': ('title',)}
admin.site.register(Post, PostAdmin)

class PageAdmin(admin.ModelAdmin):
    list_display  = ('title', 'status', direct_url)
    list_filter   = ('status',)
    search_fields = ('title', 'body')
    prepopulated_fields = {'slug': ('title',)}
admin.site.register(Page, PageAdmin)
