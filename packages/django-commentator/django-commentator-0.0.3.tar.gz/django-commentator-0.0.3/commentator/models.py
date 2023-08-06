# -*- coding: utf-8 -*-
from django.utils import timezone
from django.conf import settings
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.core import urlresolvers
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.db.models.signals import post_save

from .managers import CommentManager, ThreadManager, CommentTreeManager


class Thread(models.Model):
    content_type = models.ForeignKey(ContentType, verbose_name=_(u'content type'),
                                     related_name="content_type_set_for_%(class)s")
    object_pk = models.TextField(_('object ID'))
    content_object = generic.GenericForeignKey(
        ct_field="content_type",
        fk_field="object_pk")

    last_message = models.DateTimeField(null=True, blank=True, db_index=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = ThreadManager()

    def __unicode__(self):
        return u"Thread: %s: %s" % (self.content_type, self.content_object)

    class Meta(object):
        ordering = ('-last_message',)
        db_table = 'commentaror_threads'
        verbose_name = _('Thread')
        verbose_name_plural = _('Threads')

    def delete(self, *args, **kwargs):
        Comment.objects.filter(thread=self).delete()
        super(Thread, self).delete(*args, **kwargs)

    @property
    def comment_count(self):
        return Comment.objects.for_thread(self).count()

    @property
    def last_comment(self):
        return Comment.objects.last_comment_thread(self)

    @property
    def get_content_object_url(self):
        """
        Get a URL suitable for redirecting to the content object.
        """
        return urlresolvers.reverse(
            "commentator-url-redirect",
            args=(self.content_type_id, self.object_pk)
        )

    def get_absolute_url(self):
        return self.get_content_object_url()


class ThreadView(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_(u'User'))
    thread = models.ForeignKey(Thread, verbose_name=_(u'Thread'))

    timestamp = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        default=timezone.now())

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta(object):
        unique_together = 'user', 'thread'
        ordering = ('thread', 'created_at')
        db_table = 'commentaror_threadview'
        verbose_name = _('View')
        verbose_name_plural = _('Views')


class Comment(models.Model):
    thread = models.ForeignKey(Thread, verbose_name=_(u'Thread'))

    part_of = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        default=None,
        verbose_name=_(u'Parent'))

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_(u'User'))

    text = models.TextField(verbose_name=_(u'Comment'), blank=True, null=True)
    raw = models.TextField(verbose_name=_(u'Raw content'))

    edited = models.BooleanField(default=False, verbose_name=_(u'Edited'))
    deleted = models.BooleanField(default=False, verbose_name=_(u'Deleted'))

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(blank=True, null=True)

    path = models.CharField(max_length=255, blank=True, default='')

    objects = CommentManager()
    tree = CommentTreeManager()

    _sep = u'/'

    def __unicode__(self):
        return "%s: %s..." % (
            self.author, self.text[:49] + '...' if len(self.text) > 50 else self.text)

    class Meta(object):
        ordering = ('thread', 'created_at')
        db_table = 'commentaror_comments'
        verbose_name = _('Comment')
        verbose_name_plural = _('Comments')

    def get_absolute_url(self, anchor_pattern="#comment-%s"):
        return self.thread.get_content_object_url + (anchor_pattern % self.id)

    def save(self, *args, **kwargs):
        if not self.id:
            super(Comment, self).save(*args, **kwargs)

        self._set_path()
        super(Comment, self).save(*args, **kwargs)

    def _set_path(self):
        if self.part_of:
            self.path = "%s%s/" % (self.part_of.path, self.id)
        else:
            self.path = "%s/" % self.id

    @property
    def level(self):
        return unicode(self.path).count(self._sep)

    def roots(self):
        tree = self._default_manager.filter(part_of__isnull=True)
        return tree.filter(thread=self.thread)

    def get_path(self):
        return [self._default_manager.get(id=p).filter(thread=self.thread)
                for p in unicode(self.path).split(self._sep) if p]

    def descendants(self):
        tree = self._default_manager.filter(
            path__startswith=self.path).exclude(
            id=self.id)
        return tree.filter(thread=self.thread)

    def parent(self):
        return self.part_of

    def siblings(self):
        return [p for p in self.part_of.descendants() if p.level == self.level]

    def children(self):
        return [p for p in self.descendants() if p.level == self.level + 1]

    def is_sibling_of(self, node):
        return self.part_of == node.part_of

    def is_child_of(self, node):
        return self.part_of == node

    def is_root(self):
        return bool(self.part_of)

    def is_leaf(self):
        return self.descendants().count() == 0


def update_last_message_datetime(sender, instance, created, **kwargs):
    """
    Update Thread's last_message field when
    a new message is sent.
    """
    if not created:
        return

    Thread.objects.filter(id=instance.thread.id).update(
        last_message=instance.created_at
    )


post_save.connect(update_last_message_datetime, sender=Comment)
