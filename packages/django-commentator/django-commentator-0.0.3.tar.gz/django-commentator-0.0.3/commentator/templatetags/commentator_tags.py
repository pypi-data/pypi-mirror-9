# -*- coding: utf-8 -*-
from urlparse import urljoin
import urllib
import hashlib
import json

from django import template
from django.template.loader import render_to_string
from django.contrib.staticfiles.storage import staticfiles_storage

from ..models import *
from ..forms import *
from ..default import COMMENTATOR_CONFIG


register = template.Library()


def _line(context, node, tree, timestamp):
    new_comment = ''
    if node.created_at > timestamp:
        new_comment = ' commentator-comment-new'

    rendered = render_to_string('commentator/comment_body.html',
                                {'obj': node, 'comments': tree, 'new_comment': new_comment}, context)
    rendered = ''.join(rendered)

    return rendered


def _subtree(context, node, timestamp):
    tree = ''
    for subnode in node.children():
        tree += _subtree(
            context,
            subnode, timestamp)
    return _line(context, node, tree, timestamp)


@register.inclusion_tag('commentator/comment_wrapper.html', takes_context=True)
def comment_wrapper(context, obj):
    request = context['request']
    contenttype = ContentType.objects.get_for_model(obj)
    thread, __ = Thread.objects.get_or_create(
        object_pk=str(
            obj.pk), content_type=contenttype)
    timestamp = timezone.now()
    if request.user.is_authenticated():
        threadview, __ = ThreadView.objects.get_or_create(
            user=request.user, thread=thread)
        timestamp = threadview.timestamp
        threadview.timestamp = timezone.now()
        threadview.save()
    comments = Comment.tree.roots().filter(thread=thread)
    tree = ''
    for root_node in comments:
        tree += _subtree(
            context,
            root_node, timestamp)
    tree = "<ol class=\"comment-list\" id=\"comments\">%s</ol>\n" % tree
    return {'comments': tree, 'obj': obj, 'thread': thread,
            'form': CommentForm(), 'request': request}


@register.filter
def comment_count(obj):
    contenttype = ContentType.objects.get_for_model(obj)
    thread, __ = Thread.objects.get_or_create(
        object_pk=str(
            obj.pk), content_type=contenttype)
    comments = Comment.objects.active().filter(thread=thread).count()
    return comments


@register.simple_tag
def show_comment_count(obj):
    contenttype = ContentType.objects.get_for_model(obj)
    thread, __ = Thread.objects.get_or_create(
        object_pk=str(
            obj.pk), content_type=contenttype)
    comments = thread.comment_count
    return comments


@register.simple_tag
def show_thread_views(obj):
    contenttype = ContentType.objects.get_for_model(obj)
    thread, __ = Thread.objects.get_or_create(
        object_pk=str(
            obj.pk), content_type=contenttype)
    views = ThreadView.objects.filter(thread=thread).count()
    return views


def get_static_url():
    """Return a base static url, always ending with a /"""
    path = getattr(settings, 'STATIC_URL', None)
    if not path:
        path = getattr(settings, 'MEDIA_URL', None)
    if not path:
        path = '/'
    return path


@register.simple_tag
def commentator_css():
    """
    Template tag to print out the proper <link/> tag to include a custom .css
    """
    LINK_HTML = """<link rel="stylesheet" type="text/css" href="%s"/>"""
    css_file = urljoin(get_static_url(), 'commentator/css/default.css')
    editor_file = urljoin(get_static_url(), 'commentator/editor/editor.css')
    return LINK_HTML % css_file + LINK_HTML % editor_file


@register.simple_tag
def commentator_js():
    config = "<script type=\"text/javascript\">CommentatorConfig=%s</script>" % json.dumps(COMMENTATOR_CONFIG,
                                                                                           ensure_ascii=False)
    script_html = """<script type="text/javascript" src="%s"></script>"""
    js_file = urljoin(get_static_url(), 'commentator/js/default.js')
    editor_file = urljoin(
        get_static_url(),
        'commentator/editor/jquery.markitup.js')
    return config + script_html % js_file + script_html % editor_file


@register.tag
def gravatar_url(parser, token):
    try:
        token_parts = token.split_contents()
        args = token_parts[1:]
    except ValueError:
        raise template.TemplateSyntaxError(
            "%r tag requires at least one argument" %
            token.contents.split()[0])
    return GravatarUrlNode(*args)


class GravatarUrlNode(template.Node):

    def __init__(self, email, size=None):
        self.email = template.Variable(email)
        self.size = size

    def render(self, context):
        try:
            email = self.email.resolve(context)
            request = context.get('request')
        except template.VariableDoesNotExist:
            return ''
        except KeyError:
            raise Exception(
                'gravatar_url requires `RequestContext` or `request` in template context')
        # http://en.gravatar.com/site/implement/images/
        params = dict(
            s=self.size or getattr(settings, 'GRAVATAR_SIZE', 40),
            r=getattr(settings, 'GRAVATAR_RATING', 'pg'),
        )
        default = getattr(settings, 'GRAVATAR_DEFAULT', None)
        if default:
            if default not in (
                    '404', 'mm', 'identicon', 'monsterid', 'wavatar', 'retro', ):
                default = staticfiles_storage.url(default)
            params['d'] = default
        proto = 'http'
        host = 'www.gravatar.com'
        if request.is_secure():
            proto += 's'
            host = 'secure.gravatar.com'
        gravatar_url = proto + "://" + host + "/avatar/" + \
                       hashlib.md5(email.lower()).hexdigest() + "?"
        gravatar_url += urllib.urlencode(params)
        return gravatar_url
