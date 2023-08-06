# -*- coding: utf-8 -*-
from django.conf.urls import url, patterns


urlpatterns = patterns('commentator.views',
                       url(r'^post/$',
                           'post_comment',
                           name='commentator-post-comment'),
)

urlpatterns += patterns('',
                        url(r'^cr/(\d+)/(.+)/$',
                            'django.views.defaults.shortcut',
                            name='commentator-url-redirect'),
)
