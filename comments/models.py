from django.db import models
from django.conf import settings
from django.contrib.comments.models import Comment
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.utils.timezone import utc
from django.utils.translation import ugettext_lazy as _

from blog.models import Post, Page

from markdown import markdown
from tools.markdown_ext import RestrictiveMarkdownExtension
import hashlib
import requests
import datetime


DEFAULT_AVATAR_URL = "/static/default_avatar.png"

class KopiComment(Comment):
    AVATAR_SIZE = 48

    identifier = models.CharField(max_length=50)
    comment_html = models.TextField(editable=False, blank=True)
    session_id = models.TextField(editable=False, blank=True)
    content_owner = models.BooleanField(_('is content commented owner'), default=False)

    def get_avatar_url(self):
        try:
            if self.user_url:
                javatar = getJavatar(self.user_url)
                if javatar:
                    #print("Javatar {0}".format(javatar))
                    return javatar
            if self.user_email:
                gravatar =  getGravatar(self.user_email)
                if gravatar:
                    #print("gravatar {0}".format(gravatar))
        		return gravatar
        except requests.exceptions.ConnectionError as e:
            # not connected
            print("DEBUG: connection avatar ", e)
        except Exception as e:
            # can not reach a website, timeout
            print("DEBUG: error avatar ", e)

        #print("default {0}".format(DEFAULT_AVATAR_URL))
        return DEFAULT_AVATAR_URL


    def still_editable(self):
        """Check if a comment is not too old to be edited"""
        max_date = self.submit_date + datetime.timedelta(minutes=getattr(settings, 'COMMENT_ALTERATION_TIME_LIMIT', 15))
        return max_date > datetime.datetime.utcnow().replace(tzinfo=utc)
            

    def save(self, force_insert=False, force_update=False):
        rext = RestrictiveMarkdownExtension()
        self.comment_html = markdown(self.comment, [rext], safe_mode="escape")
        
        # check if content owner of the blog post
        if self.user and self.content_type.app_label == "blog" and self.content_type.name == "post":
            try:
                p = Post.objects.get(id=self.object_pk)
                if p.author.user == self.user:
                    self.content_owner = True
            except:
                # should never happen, are not suppose to retrieve comment
                # for non-existing content but who knows...
                print("ERROR! Post #{0} does not exist".format(self.object_pk))
                
        # check if content owner of the blog page
        if self.user and self.content_type.app_label == "blog" and self.content_type.name == "page":
            try:
                p = Page.objects.get(id=self.object_pk)
                if p.author.user == self.user:
                    self.content_owner = True
            except:
                print("ERROR! Page #{0} does not exist".format(self.object_pk))
                
        super(KopiComment, self).save(force_insert, force_update)


def getJavatar(url):
    javatar_url = "{0}/avatar.png".format(url)
    avatar = requests.get(javatar_url, timeout=1)
    if avatar.status_code == 200 and avatar.headers['content-type'][:6] == "image/":
        return javatar_url
    else:
        return False


def getGravatar(email):
    md5 = hashlib.md5(email).hexdigest()
    # on websites with SSL, use https://secure.gravatar instead
    gravatar_url = "http://www.gravatar.com/avatar/{0}?s={1}&d=404".format(md5,KopiComment.AVATAR_SIZE)
    avatar = requests.get(gravatar_url,timeout=1)
    if avatar.status_code == 200 and avatar.headers['content-type']:
        return gravatar_url
    else:
        return False


class Subscription(models.Model):
    """A visitor subscribing to recieve new comments by email"""

    content_type   = models.ForeignKey(ContentType,
            verbose_name=_('content type'),
            related_name="content_type_set_for_%(class)s")
    object_pk      = models.TextField(_('object ID'))
    email          = models.EmailField(_("subscriber's email address"), blank=True)
    manager_key    = models.TextField(_('Unique key to manage the subscription'))

    
    def generate_key(self):
        import string, random
        key_length = getattr(settings,'COMMENT_SUBSCRIPTION_KEY_LENGTH', 20)
        key = ''.join(random.choice(string.digits+string.ascii_letters) for i in range(key_length))
        subscriptions = Subscription.objects.filter( manager_key=key )
        cpt = 0
        while len(subscriptions) > 0 and cpt < 100:
            # Try until find a unique key
            # statistically impossible with a big key size
            # but I don't want an infinite loop so no more than 100 try
            key = ''.join(random.choice(string.digits+string.ascii_letters) for i in range(key_length))
            subscriptions = Subscription.objects.filter( manager_key=key )
            cpt += 1
            
        if len(subscriptions) > 0:
            # sorry you have to fail
            return None
        return key

    def save(self, force_insert=False, force_update=False):
        if not self.manager_key:
            self.manager_key = self.generate_key()
        super(Subscription, self).save(force_insert, force_update)

    def get_unsubscribe_url(self):
        return reverse('comment-sub-remove',args=[self.manager_key])
