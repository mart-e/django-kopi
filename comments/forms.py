from django import forms
from django.contrib.comments.models import Comment
from django.contrib.comments.forms import CommentForm
from django.utils.translation import ugettext_lazy as _
from comments.models import KopiComment, Subscription

class KopiCommentForm(CommentForm):
    #identifier    = forms.CharField(label=_("Identifier"), max_length=50, required=True)
    # overwrite for required=False
    name          = forms.CharField(label=_("Name"), max_length=50, required=False)
    email         = forms.EmailField(label=_("Email address"), required=False)

    class Meta:
        model = KopiComment
        exclude = ('content_type', 'object_pk', 'site', 'user', 'is_public',
            'user_name', 'user_email', 'user_url', 'submit_date', 'ip_address',
            'is_removed',)

    def get_comment_model(self):
        # Use our custom comment model instead of the built-in one.
        return KopiComment

    def get_comment_create_data(self):
        # Use the data of the superclass
        data = super(KopiCommentForm, self).get_comment_create_data()
        data['identifier'] = self.computeIdentifier(data.get('user_name'), data.get('user_email'),data.get('user_url'))
        return data

    def clean(self):
        self.cleaned_data = super(KopiCommentForm, self).clean()
        name = self.cleaned_data.get('name') 
        email = self.cleaned_data.get('email')
        url = self.cleaned_data.get('url')
        # if not name and not email and not url:
        #     self._errors
        #     raise forms.ValidationError(_("Please fill at least of of the name, email or url fields"))
        return self.cleaned_data
    
    def computeIdentifier(self, name=None, email=None, url=None):
        """From the identifier, compute the other fields"""
        if not name and not email and not url:
            return "Anonymous"

        if name:
            return name

        if email:
            return email.split('@')[0]

        return url.split('/')[2][:20]

                
class SubscriptionForm(forms.ModelForm):

    class Meta:
        model = Subscription
        exclude = ('manager_key',)

    
