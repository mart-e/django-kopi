import datetime

from django.conf import settings
from django.contrib.comments.models import Comment
from django.contrib.comments.views import comments as contrib_comments
from django.contrib.comments.views.utils import next_redirect, confirmation_view
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db import models
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_POST
from django.utils.timezone import utc

from comments.models import KopiComment
from comments.forms import KopiCommentForm
from tools.shortcuts import render, redirect
from httpbl.views import HttpBLMiddleware

MAX_SUBMIT_DATE = datetime.datetime.utcnow().replace(tzinfo=utc) - datetime.timedelta(
            minutes=getattr(settings, 'COMMENT_ALTERATION_TIME_LIMIT', 15)*10)


def comment_edit(request, object_id, template_name='comments/edit.html'):
    # comment = get_object_or_404(KopiComment, pk=object_id, user=request.user)
    comment = get_object_or_404(KopiComment, pk=object_id)

    if MAX_SUBMIT_DATE > comment.submit_date:
        return comment_error(request, error_message='Too old comment')

    if comment.session_id != request.session.session_key:
        return comment_error(request, error_message='You are not the author of the comment or your session as expired')

    if request.method == 'POST':
        form = KopiCommentForm(request.POST, data=comment)
        if form.is_valid():
            form.save()
            return redirect(request, comment.content_object)
    else:
        form = KopiCommentForm(comment)
    return render(request, template_name, {
        'form': form,
        'comment': comment,
    })


def comment_remove(request, object_id, template_name='comments/delete.html'):
    comment = get_object_or_404(KopiComment, pk=object_id, user=request.user)

    if MAX_SUBMIT_DATE > comment.submit_date:
        return comment_error(request, error_message='Too old comment')

    if comment.session_id != request.session.session_key:
        return comment_error(request, error_message='You are not the author of the comment or your session as expired')

    if request.method == 'POST':
        comment.delete()
        return redirect(request, comment.content_object)
    return render(request, template_name, {'comment': comment})


def comment_error(request, error_message='You can not change this comment.',
        template_name='comments/error.html'):
    return render(request, template_name, {'error_message': error_message})


# owerwrite the post_comment form to redirect to NEXTURL#cID and spam checking
def custom_comment_post(request, next=None, using=None):

    # Check if IP not blacklisted
    httpbl = HttpBLMiddleware()
    response = httpbl.process_request(request)
    if response:
        # User blacklisted
        return response

    # original post comment function
    response = contrib_comments.post_comment(request, next, using)

    if type(response) == HttpResponseRedirect:
        redirect_path, comment_id  = response.get('Location').split( '?c=' )
        # check if the comment was saved
        comment = KopiComment.objects.get( id=comment_id )
        if comment:
            # set the session id to the current one to allow edit
            comment.session_id = request.session.session_key
            comment.save()
            return HttpResponseRedirect( comment.get_absolute_url("#c%(id)s") )
    
    return response

