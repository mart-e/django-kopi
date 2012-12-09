import datetime
import time

from django.conf import settings
#from django.contrib.comments.forms import CommentForm
from django.contrib.comments.models import Comment
from django.contrib.comments.views import comments as contrib_comments
from django.contrib.comments.views.utils import next_redirect, confirmation_view
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.core.mail import send_mail
from django.db import models
from django.forms.models import model_to_dict
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.template import Context, RequestContext
from django.template.loader import get_template
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_POST
from django.utils.timezone import utc
from django.utils.translation import ugettext_lazy as _

from blog.models import Post, Page
from comments.models import KopiComment, Subscription
from comments.forms import KopiCommentForm
from tools.shortcuts import render, redirect
from httpbl.views import HttpBLMiddleware

MAX_SUBMIT_DATE = datetime.datetime.utcnow().replace(tzinfo=utc) - datetime.timedelta(
            minutes=getattr(settings, 'COMMENT_ALTERATION_TIME_LIMIT', 15))


def comment_edit(request, object_id, template_name='comments/edit.html'):
    """Edit the comment"""

    comment = get_object_or_404(KopiComment, pk=object_id)

    # check if can edit the comment
    if MAX_SUBMIT_DATE > comment.submit_date:
        return comment_error(request, error_message=_('Too old comment'))

    if comment.session_id != request.session.session_key:
        return comment_error(request, error_message=_('You are not the author of the comment or your session has expired'))

    # is the user submiting the form
    if request.method == 'POST':
        form = KopiCommentForm(comment, data=request.POST)
        if form.is_valid():
            # get the data in a processable form
            data = form.get_comment_create_data()
            comment.user_email = data['user_email']
            comment.user_name = data['user_name']
            comment.user_url = data['user_url']
            comment.comment = data['comment']
            comment.identifier = data['identifier']
            comment.save()
            return redirect(request, comment.content_object)
        else:
            pass
            #print(form.errors)

    else:
        comment_dic = model_to_dict(comment)
        comment_dic['name'] = comment.user_name
        comment_dic['email'] = comment.user_email
        comment_dic['url'] = comment.user_url
        form = KopiCommentForm(comment, data=comment_dic, initial=None)  
        security_dict = form.generate_security_data()
        # recreate the security fields
        form.data['content_type'] = security_dict['content_type']
        form.data['object_pk'] = security_dict['object_pk']
        form.data['timestamp'] = security_dict['timestamp']
        form.data['security_hash'] = security_dict['security_hash']

    return render(request, template_name, {
        'form': form,
        'comment': comment,
    })


def comment_remove(request, object_id, template_name='comments/delete.html'):
    comment = get_object_or_404(KopiComment, pk=object_id)

    if MAX_SUBMIT_DATE > comment.submit_date:
        return comment_error(request, error_message=_('Too old comment'))

    if comment.session_id != request.session.session_key:
        return comment_error(request, error_message=_('You are not the author of the comment or your session has expired'))

    if request.method == 'POST':
        comment.delete()
        return redirect(request, comment.content_object)
    return render(request, template_name, {'comment': comment})


def comment_error(request, error_message=_('You can not change this comment.'),
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
        redirect_path, comment_id = response.get('Location').split('?c=')
        # check if the comment was saved
        comment = KopiComment.objects.get( id=comment_id )
        if comment:
            # set the session id to the current one to allow edit
            comment.session_id = request.session.session_key
            comment.save()

            if 'subscribe' in request.POST:
                comment_subscribe(comment)
            return HttpResponseRedirect( comment.get_absolute_url("#c%(id)s") )
    
    return response


## Comment subscription

def comment_subscribe(comment):
    subscription = Subscription()
    subscription.content_type = comment.content_type
    subscription.object_pk = comment.object_pk
    subscription.email = comment.email
    subscription.manager_key = subscription.generate_key()
    subscription.save()

    if subscription.content_type.name == "post":
        p = Post.objects.get(id=subscription.object_pk)
    elif subscription.content_type.name == "page":
        p = Page.objects.get(id=subscription.object_pk)
    else:
        raise Exception("Unknown subscription content type {0}".format(subscription.content_type.name))
    
    title = p.title
    object_url = p.get_absolute_url()
    author = p.author.user.username
    author_email = p.author.user.email
    author_url = p.author.url
            
    subject = _("Confirmation subscription")
    plaintext = get_template('mail/mail_confirm_sub.txt')
    message_context = Context({'title':title,
                               'object_url':object_url,
                               'unsubscribe_url':subscription.get_unsubscribe_url(),
                               'author':author,
                               'author_url':author_url})
    text_content = plaintext.render(message_context)

    print({'title':title,
           'object_url':object_url,
           'unsubscribe_url':subscription.get_unsubscribe_url(),
           'author':author,
           'author_url':author_url})

    try:
        send_mail(subject, text_content, author_email, [subscription.email])
    except Exception as e:
        print("Error while sending mail", e)

def comment_sub_post(request, next='/'):
    if request.method == 'POST':
        form = SubscriberForm(request.POST)
        if form.is_valid():
            subscription = form.save(commit=False)
            subscription.manager_key = subscription.generate_key()
            subscription.save()

            if subscription.content_type.name == "post":
                p = Post.objects.get(id=subscription.object_pk)
                title = p.title
                object_url = p.get_url()
                author = p.author.user.username
                author_email = p.author.user.email
                author_url = p.author.url
            else:
                raise Exception("Unknown subscription content type {0}".format(subscription.content_type.name))
            
            subject = _("Confirmation subscription")
            plaintext = get_template('email_confim_sub.txt')
            message_context = Context({'title':title,
                                   'object_url':object_url,
                                   'unsubscribe_url':subscription.get_unsubscribe_url(),
                                   'author':author,
                                   'author_url':author_url})
            text_content = plaintext.render(message_context)

            send_mail(subject, text_content, author_email, [subscription.email])

            return HttpResponseRedirect(next)
    
    return  HttpResponseRedirect(next)

def comment_sub_manage(request, object_id):
    """Manage the comment subscription to an object

    Provide small summary and unsubscribe link"""
    subscription = get_object_or_404(Subscription, manager_key=object_id)
    return render(request, "subscription_manage.html", {'sub': subscriber})

def comment_sub_remove(request, object_id):
    """Unsubscribe to comments to an object"""
    subscription = get_object_or_404(Subscription, manager_key=object_id)
    subscription.delete()
    return render(request, "subscription_remove.html", {})
