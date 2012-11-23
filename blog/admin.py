from django.contrib import admin
from blog.models import *

class PostAdmin(admin.ModelAdmin):
    list_display  = ('title', 'publish', 'status')
    list_filter   = ('publish', 'status')
    search_fields = ('title', 'body')
    prepopulated_fields = {'slug': ('title',)}
admin.site.register(Post, PostAdmin)

class PageAdmin(admin.ModelAdmin):
    list_display  = ('title', 'status')
    list_filter   = ('status',)
    search_fields = ('title', 'body')
    prepopulated_fields = {'slug': ('title',)}
admin.site.register(Page, PageAdmin)
