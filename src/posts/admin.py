from django.contrib import admin
from .models import Post
# Register your models here.

class PostAdmin(admin.ModelAdmin):
    class Meta:
        model = Post
    list_display = ('title', 'updated', 'timestamp')
    list_display_links = ('updated',)
    list_filter = ('updated', 'timestamp')
    list_editable = ['title']
    search_fields = ['title', 'content']

admin.site.register(Post, PostAdmin)
