from django.forms import ModelForm
from django.contrib.comments.models import Comment
from django.contrib.comments.forms import CommentForm
from comments.models import KopiComment

class KopiCommentForm(CommentForm):
    class Meta:
        model = KopiComment
        exclude = ('content_type', 'object_pk', 'site', 'user', 'is_public',
            'user_name', 'user_email', 'user_url', 'submit_date', 'ip_address',
            'is_removed',)

    def get_comment_model(self):
        # Use our custom comment model instead of the built-in one.
        return KopiComment

    def get_comment_create_data(self):
        # Use the data of the superclass, and add in the title field
        data = super(KopiCommentForm, self).get_comment_create_data()
        # data['title'] = self.cleaned_data['title']
        return data