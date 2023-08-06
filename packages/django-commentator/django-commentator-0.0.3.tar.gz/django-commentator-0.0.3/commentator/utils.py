# -*- coding: utf-8 -*-
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings


def send_mail(email, subject, text_template, html_template, context):
    text_content = render_to_string(text_template, context)
    html_content = render_to_string(html_template, context)
    msg = EmailMultiAlternatives(subject, text_content, settings.EMAIL_FROM,
                                 [email])
    msg.attach_alternative(html_content, 'text/html')
    msg.send()
