# -*- coding: utf-8 -*-

from django.utils import timezone
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_protect
from django.http import HttpResponseRedirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.utils.html import remove_tags
from django.views.decorators.http import require_http_methods

from .models import Comment, Thread, ThreadView
from .forms import CommentForm
from .utils import send_mail


@login_required
@csrf_protect
@require_http_methods(["GET", "POST"])
def post_comment(request, *args, **kwargs):
    if request.is_ajax() and 'action' in request.REQUEST:
        form = CommentForm(data=request.REQUEST)

        if request.REQUEST['action'] == 'save':
            if form.is_valid():
                raw = form.cleaned_data['raw']
                comment = form.save(commit=False)
                comment.text = remove_tags(raw, "script link div")
                comment.author = request.user

                comment.save()
                resp = {
                    'success': True,
                    'message': "",
                    'data': {
                        'comment': render_to_string('commentator/comment_body.html',
                                                    {'obj': comment, 'request': request})
                    }
                }
                if comment.part_of and comment.author != comment.part_of.author:
                    send_mail(comment.part_of.author.email, u'Ответ на ваш комментарий',
                              'commentator/emails/email_reply.txt', 'commentator/emails/email_reply.html',
                              {'comment': comment})
                return JsonResponse(resp, status=201)
            else:
                resp = {
                    'success': False,
                    'message': "Something went wrong!",
                    'data': {
                        'comments': ''
                    },
                    'errors': form.errors
                }
                return JsonResponse(resp, status=500)
        elif request.REQUEST['action'] == 'preview':
            if form.is_valid():
                raw = form.cleaned_data['raw']
                comment = form.save(commit=False)
                comment.text = remove_tags(raw, "script", "link", "div")
                comment.author = request.user

                resp = {
                    'success': True,
                    'message': "",
                    'data': {
                        'preview': render_to_string('commentator/comment_body.html',
                                                    {'obj': comment, 'request': request})
                    }
                }
                return JsonResponse(resp)
            else:
                resp = {
                    'success': False,
                    'message': "Something went wrong!",
                    'data': {
                        'comments': ''
                    },
                    'errors': form.errors
                }
                return JsonResponse(resp, status=500)
        elif request.REQUEST['action'] == 'getlist' and 'thread' in request.REQUEST:
            thread, __ = Thread.objects.get_or_create(
                id=int(
                    request.POST['thread']))
            if request.user.is_authenticated():
                threadview, __ = ThreadView.objects.get_or_create(
                    user=request.user, thread=thread)
                timestamp = threadview.timestamp
                threadview.timestamp = timezone.now()
                threadview.save()
            else:
                timestamp = timezone.now()
            comments = Comment.objects.filter(
                thread=thread,
                created_at__gte=timestamp)
            json_comments = {}
            for c in comments:
                if c.created_at > timestamp:
                    new_comment = ' commentator-comment-new'
                else:
                    new_comment = ''
                json_comments[c.id] = render_to_string('commentator/comment_body.html',
                                                       {'obj': c, 'new_comment': new_comment, 'request': request})

            resp = {
                'success': True,
                'message': "",
                'data': {
                    'comments': json_comments
                }
            }
            return JsonResponse(resp)
        else:
            resp = {
                'success': False,
                'message': "Not exist action",
                'data': {
                    'comments': ''
                }
            }
            return JsonResponse(resp, status=500)
    else:
        return HttpResponseRedirect('/')
