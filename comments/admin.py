from django.contrib import admin
from comments.models import KopiComment, Subscription

def get_identifier(obj):
    if obj.identifier:
        return obj.identifier
    if not obj.user_name and not obj.user_email and not obj.user_url:
        return "Anonymous"
    if obj.user_name:
        return obj.user_name
    
    if obj.user_email:
        return obj.user_email.split('@')[0]

    return obj.user_url.split('/')[2][:20]
get_identifier.short_description = 'Identifier'

def direct_url(obj):
    return u'<a href="%s">#</a>' % (obj.get_absolute_url())
direct_url.short_description = 'url'
direct_url.allow_tags = True

class KopiCommentAdmin(admin.ModelAdmin):
    list_display  = (get_identifier, 'comment', 'submit_date', 'is_public', direct_url)
    list_filter = ('identifier', 'comment', 'submit_date')
    search_fields = ('title', 'body')
    ordering = ['-submit_date',]

admin.site.register(KopiComment,KopiCommentAdmin)
admin.site.register(Subscription)
