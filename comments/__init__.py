from comments.models import KopiComment
from comments.forms import KopiCommentForm

def get_model():
    return KopiComment

def get_form():
    return KopiCommentForm