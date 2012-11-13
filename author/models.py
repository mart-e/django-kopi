from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
     
class Author(models.Model):
    user = models.ForeignKey(User, unique=True)
    url = models.URLField(_('Profile address'), verify_exists=False, blank=True)

    class Meta:
        verbose_name = _('author')
        verbose_name_plural = _('authors')
        ordering  = ('-user',)

    def __unicode__(self):
        return u'%s' % self.user
