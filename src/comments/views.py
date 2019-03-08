from django.contrib import messages
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.decorators import login_required
from .models import Comment
from .forms import CommentForm

# Create your views here.
@login_required(login_url='/login')
def comment_delete(request, id):
    try:
        instance = Comment.objects.get(id=id)
    except:
        raise Http404

    if instance.user != request.user:
        response = HttpResponse('You dont have permission')
        response.status_code = 403
        return response

    if request.method == "POST":
        parent_obj_url = instance.content_object.get_absolute_url()
        instance.delete()
        messages.success(request, 'COMMENT DELETED')
        return HttpResponseRedirect(parent_obj_url)
    context_data = {
        'object': instance,
    }
    return render(request,'confirm_delete.html', context_data)

def comment_thread(request, id):
    try:
        instance = Comment.objects.get(id=id)
    except:
        raise Http404

    if not instance.is_parent:
        instance = instance.parent
    content_obj = instance.content_object
    content_id = instance.content_object.id
    initial_data = {
        'content_type': instance.content_type,
        'object_id': instance.object_id
    }
    comment_form = CommentForm(request.POST or None, initial=initial_data)
    if comment_form.is_valid() and request.user.is_authenticated():
        c_type = comment_form.cleaned_data.get('content_type')
        content_type = ContentType.objects.get(model=c_type)
        obj_id = comment_form.cleaned_data.get('object_id')
        content_data = comment_form.cleaned_data.get('content')
        parent_obj = None
        try:
            parent_id = int(request.POST.get('parent_id'))
        except:
            parent_id = None

        if parent_id:
            parent_qs = Comment.objects.filter(id=parent_id)
            if parent_qs.exists() and parent_qs.count() == 1:
                parent_obj = parent_qs.first()
        new_comment, created = Comment.objects.get_or_create(
            user = request.user,
            content_type = content_type,
            object_id = obj_id,
            content = content_data,
            parent = parent_obj
        )
        return HttpResponseRedirect(new_comment.content_object.get_absolute_url())
    context = {
        'title': 'thread',
        'comment': instance,
        'form': comment_form
    }
    return render(request,'comment_thread.html', context)
