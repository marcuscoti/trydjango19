from __future__ import unicode_literals
from django.conf import settings
from django.db import models
from django.core.urlresolvers import reverse
from django.db.models.signals import pre_save
from django.utils.text import slugify
from django.utils import timezone
from django.utils.safestring import mark_safe
from markdown_deux import markdown
from django.contrib.contenttypes.models import ContentType
from .utils import get_read_time


# Create your models here.


class PostManager(models.Manager):

    def active(self):
        return super(PostManager, self).filter(draft=False).filter(publish__lte=timezone.now())

def user_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return "%s/%s" %(instance.user.id, filename)

class Post(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, default=1)
    title = models.CharField(max_length=120)
    slug = models.SlugField(unique=True)
    image = models.ImageField(upload_to=user_directory_path, null=True, blank=True, height_field="height_field", width_field="width_field")
    height_field = models.IntegerField(default=0)
    width_field = models.IntegerField(default=0)
    draft = models.BooleanField(default=False)
    publish = models.DateField(auto_now=False,auto_now_add=False)
    read_time = models.TimeField(blank=True, null=True)
    content = models.TextField(max_length=250)
    updated = models.DateTimeField(auto_now=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    objects = PostManager()

    def __unicode__(self):
        return self.title

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('posts:detail', kwargs={'slug': self.slug})

    def get_markdown(self):
        content = self.content
        return mark_safe(markdown(content))

    @property
    def get_content_type(self):
        instance  = self
        content_type = ContentType.objects.get_for_model(instance.__class__)
        return content_type

    # @property
    # def comments(self):
    #     instance = self
    #     comments = Comment.objects.get_by_instance(instance)
    #     return comments

    class Meta:
        ordering = ['-timestamp', '-updated']


def create_slug(title, slug=None, kc=1):
    if slug==None:
        slug = slugify(title)
    if Post.objects.filter(slug=slug).exists():
        kc += 1
        slug = "%s-%s" % (slug, kc)
        return create_slug(title, slug, kc)
    return slug

def pre_save_post_receiver(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = create_slug(instance.title)
    if instance.content:
        instance.read_time = get_read_time(instance.get_markdown())



pre_save.connect(pre_save_post_receiver, Post)
