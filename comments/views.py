import datetime

from django.conf import settings
from django.contrib.comments.models import Comment
from django.contrib.comments.views import comments as contrib_comments
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404

from comments.forms import CommentForm
from tools.shortcuts import render, redirect
from httpbl.views import HttpBLMiddleware


DELTA = datetime.datetime.now() - datetime.timedelta(
            minutes=getattr(settings, 'COMMENT_ALTERATION_TIME_LIMIT', 15))


def comment_edit(request, object_id, template_name='comments/edit.html'):
    comment = get_object_or_404(Comment, pk=object_id, user=request.user)

    if DELTA > comment.submit_date:
         return comment_error(request)

    if request.method == 'POST':
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            return redirect(request, comment.content_object)
    else:
        form = CommentForm(instance=comment)
    return render(request, template_name, {
        'form': form,
        'comment': comment,
    })


def comment_remove(request, object_id, template_name='comments/delete.html'):
    comment = get_object_or_404(Comment, pk=object_id, user=request.user)

    if DELTA > comment.submit_date:
         return comment_error(request)

    if request.method == 'POST':
        comment.delete()
        return redirect(request, comment.content_object)
    return render(request, template_name, {'comment': comment})


def comment_error(request, error_message='You can not change this comment.',
        template_name='comments/error.html'):
    return render(request, template_name, {'error_message': error_message})


# owerwrite the post_comment form to redirect to NEXTURL#cID
def custom_comment_post(request, next=None, using=None):
    httpbl = HttpBLMiddleware()
    response = httpbl.process_request(request)
    if response:
        return response

    response = contrib_comments.post_comment(request, next, using)

    if type(response) == HttpResponseRedirect:
        redirect_path, comment_id  = response.get('Location').split( '?c=' )
        comment = Comment.objects.get( id=comment_id )
        if comment:
            return HttpResponseRedirect( comment.get_absolute_url("#c%(id)s") )
    
    return response
