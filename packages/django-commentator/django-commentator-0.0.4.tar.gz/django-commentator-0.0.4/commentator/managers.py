# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.utils.encoding import force_text


class ThreadManager(models.Manager):
    def for_model(self, model):
        """
        QuerySet for all threads for a particular model (either an instance or
        a class).
        """
        ct = ContentType.objects.get_for_model(model)
        qs = self.get_queryset().filter(content_type=ct)
        if isinstance(model, models.Model):
            qs = qs.filter(object_pk=force_text(model._get_pk_val()))
        return qs


class CommentManager(models.Manager):
    def deleted(self):
        """
        QuerySet for all deleted comments.
        """
        return self.get_queryset().filter(deleted=True)

    def active(self):
        """
        QuerySet for all active comments.
        """
        return self.get_queryset().filter(deleted=False)

    def for_thread(self, thread):
        """
        QuerySet for all active comments in tread.
        """
        return self.active().filter(thread=thread).order_by('id')

    def last_comment(self):
        """
        QuerySet for return las comment.
        """
        return self.active().order_by('-created_at')[0]

    def last_comment_thread(self, thread):
        """
        QuerySet for return las comment in thread.
        """
        return self.for_thread(thread).order_by('-created_at')[0]


class CommentTreeManager(models.Manager):
    def roots(self):
        return self.get_queryset().filter(part_of__isnull=True)
