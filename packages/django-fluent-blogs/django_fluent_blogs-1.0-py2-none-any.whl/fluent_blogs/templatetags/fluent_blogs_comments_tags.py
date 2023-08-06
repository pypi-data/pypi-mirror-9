"""
A simple wrapper library, that makes sure that the template
``fluent_blogs/entry_detail/comments.html`` can still be rendered
when ``django.contrib.comments`` is not included in the site.

This way, project authors can easily use an online commenting system
(such as DISQUS or Facebook comments) instead.
"""
from django.template import Library
from fluent_utils.django_compat import is_installed

# Expose the tag library in the site.
# If `django.contrib.comments` is not used, this library can provide stubs instead.
# Currently, the real tags are exposed as the template already checks for `object.comments_are_open`.
# When a custom template is used, authors likely choose the desired commenting library instead.

if is_installed('django.contrib.comments'):
    from django.contrib.comments.templatetags.comments import register
elif is_installed('django_comments'):
    from django_comments.templatetags.comments import register
else:
    register = Library()
