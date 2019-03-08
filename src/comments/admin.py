from django.contrib import admin
from .models import Comment

# Register your models here.


class CommentAdmin(admin.ModelAdmin):
    class Meta:
        model = Comment

#admin.site.register(Post, PostAdmin)
admin.site.register(Comment)
