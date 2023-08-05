==================================
ChainableManager for Django Models
==================================

Allows chaining of custom model Manager methods, without jumping through
QuerySet hoops.

Installing
==========

Simply install the package using ``pip``::

    pip install django-chainable-manager

Using
=====

Create a Manager that extends ``chainablemanager.ChainableManager``:

.. code:: python

    from django.db import models
    from chainablemanager.manager import ChainableManager

    class PostManager(ChainableManager):
        class QuerySetMixin(object):
            def published(self):
                return self.filter(publish_date__gte=datetime.date.today())

            def written_by(self, user):
                return self.filter(author=user)

    class Post(models.Model):
        title = models.CharField(max_length=255)
        content = models.TextField()
        publish_date = models.DateField()
        author = models.ForeignKey('auth.User')

        objects = PostManager()

Now use it where ever you need it:

.. code:: python

    from .models import Post

    my_published_posts = Post.objects.written_by(request.user).published()
