from __future__ import unicode_literals
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.conf import settings
from django.db import models
# Create your models here.


class CommentManager(models.Manager):
    def get_by_instance(self, instance):
        content_type = ContentType.objects.get_for_model(instance.__class__)
        obj_id = instance.id
        qs = super(CommentManager, self).filter(content_type=content_type, object_id=obj_id).filter(parent=None)
        return qs

class Comment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, default=1)
    #post = models.ForeignKey(Post)

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    parent = models.ForeignKey('self', blank=True, null=True)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    objects = CommentManager()

    class Meta:
        ordering = ['-timestamp']

    def children(self):
        return Comment.objects.filter(parent=self)

    @property
    def is_parent(self):
        if self.parent is not None:
            return False
        else:
            return True

    @property
    def get_content_type(self):
        instance = self
        content_type = ContentType.objects.get_for_model(instance.__class__)
        return content_type

    def get_absolute_url(self):
        return reverse('comments:comment_thread', kwargs={'id': self.pk})

    def get_delete_url(self):
        return reverse('comments:comment_delete', kwargs={'id': self.pk})

    def __unicode__(self):
        return str(self.user.username)

    def __str__(self):
        return str(self.user.username)

