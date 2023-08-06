# -*- coding: utf-8 -*-
from django.conf import settings
from django.core.urlresolvers import reverse

COMMENTATOR_CONFIG = {
    'staticUrl': settings.STATIC_URL,
    'actionUrl': reverse('commentator-post-comment'),
    'close_all_message': "закрыть все",
    'tpanel': 1,
    'enable_editor': 1,
    'editor': {
        'onTab': {
            'keepDefault': False,
            'replaceWith': "\t"
        },
        'markupSet': [
            {
                'name': "Bold",
                'className': "btn-bold",
                'key': "B",
                'openWith': "<b>",
                'closeWith': "</b>"
            }, {
                'name': "Italic",
                'className': "btn-italic",
                'key': "I",
                'openWith': "<i>",
                'closeWith': "</i>"
            }, {
                'name': "Underline",
                'className': "btn-underline",
                'key': "U",
                'openWith': "<u>",
                'closeWith': "</u>"
            }, {
                'name': "Stroke through",
                'className': "btn-stroke",
                'key': "S",
                'openWith': "<s>",
                'closeWith': "</s>"
            }, {
                'separator': "---------------"
            }, {
                'name': "Quote",
                'className': "btn-quote",
                'openWith': "<blockquote>",
                'closeWith': "</blockquote>"
            }, {
                'name': "Code",
                'className': "btn-code",
                'openWith': "<code>",
                'closeWith': "</code>"
            }, {
                'name': "Link",
                'className': "btn-link",
                'openWith': "<a href=\"[![Link:!:http://]!]\">",
                'closeWith': "</a>"
            }, {
                'name': "Picture",
                'className': "btn-picture",
                'replaceWith': "<img src=\"[![Source:!:http://]!]\" />"
            }
        ]
    },
    'thread_depth': 10
}

COMMENTATOR_REPLY_SUBJECT = u'Ответ на ваш комментарий'
