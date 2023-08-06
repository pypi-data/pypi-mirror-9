# -*- coding: utf-8 -*-
from django.contrib import admin

from .models import Thread, Comment, ThreadView


admin.site.register(Thread)
admin.site.register(Comment)
admin.site.register(ThreadView)
