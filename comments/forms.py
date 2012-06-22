from django import forms
from django.contrib.comments.models import Comment
from django.contrib.comments.forms import CommentForm
from django.utils.translation import ugettext_lazy as _
from comments.models import KopiComment

class KopiCommentForm(CommentForm):
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
        return data

    def clean_name(self):
        # cleaned_data = super(KopiCommentForm, self).clean()
        print(self.cleaned_data)
        if not self.cleaned_data['name'] and 'email' not in self.cleaned_data and 'url' not in self.cleaned_data:
            raise forms.ValidationError(_("Please fill at least of of the name, email or url fields"))
        return cleaned_data