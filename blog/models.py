from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from tagging.fields import TagField
from author.models import Author

from markdown import markdown

import datetime

class Post(models.Model):
    """Post model."""
    STATUS_CHOICES = (
        (1, _('Draft')),
        (2, _('Public')),
    )
    title = models.CharField(_('title'), max_length=200)
    slug = models.SlugField(_('slug'), unique_for_date='publish')
    author = models.ForeignKey(Author, blank=True, null=True)
    body = models.TextField(_('body'), )
    body_html = models.TextField(editable=False, blank=True)
    tease = models.TextField(_('tease'), blank=True, help_text=_('Concise text suggested. Does not appear in RSS feed.'))
    tease_html = models.TextField(editable=False, blank=True)
    status = models.IntegerField(_('status'), choices=STATUS_CHOICES, default=1)
    allow_comments = models.BooleanField(_('allow comments'), default=True)
    publish = models.DateTimeField(_('publish'), default=datetime.datetime.now)
    created = models.DateTimeField(_('created'), auto_now_add=True)
    modified = models.DateTimeField(_('modified'), auto_now=True)
    tags = TagField()

    class Meta:
        verbose_name = _('post')
        verbose_name_plural = _('posts')
        db_table  = 'blog_posts'
        ordering  = ('-publish',)
        get_latest_by = 'publish'

    def __unicode__(self):
        return u'%s' % self.title
        
    @models.permalink
    def get_absolute_url(self):
        from time import strftime
        return ('blog_post_detail', [
            self.publish.year,
            self.publish.strftime('%m'),
            self.publish.day,
            self.slug
        ])

    def get_previous_post(self):
        return self.get_previous_by_publish(status__gte=2)

    def get_next_post(self):
        #print(self.title, "next", self.get_next_by_publish(status__gte=2))
        return self.get_next_by_publish(status__gte=2)

    def save(self, force_insert=False, force_update=False):
        self.body_html = markdown(self.body)
        self.tease_html = markdown(self.tease)
        super(Post, self).save(force_insert, force_update)
        
        
        
class Page(models.Model):
    """Page model.
    
    In opposition to a Post, a Page is a static dateless entry."""
    STATUS_CHOICES = (
        (1, _('Draft')),
        (2, _('Public')),
    )
    title = models.CharField(_('title'), max_length=200)
    slug = models.SlugField(_('slug'), unique_for_date='publish')
    author = models.ForeignKey(Author, blank=True, null=True)
    body = models.TextField(_('body'), )
    body_html = models.TextField(editable=False, blank=True)
    tease_html = models.TextField(editable=False, blank=True)
    status = models.IntegerField(_('status'), choices=STATUS_CHOICES, default=1)
    allow_comments = models.BooleanField(_('allow comments'), default=False)
    
    
    class Meta:
        verbose_name = _('page')
        verbose_name_plural = _('pages')
        db_table  = 'blog_pages'
        ordering  = ('-title',)
        get_latest_by = 'publish'

    def __unicode__(self):
        return u'%s' % self.title
        
    @models.permalink
    def get_absolute_url(self):
        return ('blog_page_detail', [
            self.slug
        ])

    def save(self, force_insert=False, force_update=False):
        self.body_html = markdown(self.body)
        super(Page, self).save(force_insert, force_update)

