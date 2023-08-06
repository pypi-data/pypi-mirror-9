Not for production
==================

Commentaries system for Django
==============================

What's that
-----------

*django-commentator* is a reusable commentaries application for Django


Dependence
----------

- `Django >= 1.7`

Getting started
---------------

- Install *django-commentator*:

```pip install django-commentator```

- Add `'commentator'` to INSTALLED_APPS.
- Add `url(r'^comments/', include('commentator.urls')),` to urlpatterns.
- Add `{% commentator_css %}` to head block in you template.
- Add `{% commentator_js %}` to footer block in you template.
- Add `{% load commentator_tags %}` to you template.
- Use `{% comment_wrapper obj %}` for view comments.



Contributing
------------

1. Fork it!
2. Create your feature branch: `git checkout -b my-new-feature`
3. Commit your changes: `git commit -am 'Add some feature'`
4. Push to the branch: `git push origin my-new-feature`
5. Submit a pull request =]