from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.utils import timezone
from django.db.models import Q
from urllib import quote_plus
from models import Post
from comments.models import Comment
from comments.forms import CommentForm
from django.contrib.contenttypes.models import ContentType
from forms import PostForm
from .utils import get_read_time, count_words
from django.contrib.auth.decorators import login_required
# Create your views here.

@login_required(login_url='/login')
def posts_create(request):
    if not request.user.is_staff or not request.user.is_superuser:
        return Http404()
    form = PostForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        instance = form.save(commit=False)
        instance.user = request.user
        instance.save()
        messages.success(request, 'SUCCESS')
        return redirect('posts:list')
    context = {
        'form': form,
    }
    return render(request, 'post_create.html', context)

def posts_detail(request, slug):
    obj = get_object_or_404(Post, slug=slug)
    if obj.draft or obj.publish > timezone.now().date():
        if not request.user.is_staff or not request.user.is_superuser:
            raise Http404
    share_string = quote_plus(obj.content)
    print get_read_time(obj.get_markdown())
    comments = Comment.objects.get_by_instance(obj)
    initial_data = {
        'content_type': obj.get_content_type,
        'object_id': obj.id
    }
    comment_form = CommentForm(request.POST or None, initial=initial_data)
    if comment_form.is_valid():
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

    #comments = obj.comments
    context = {
        'title': 'DETAIL',
        'object': obj,
        'share_string': share_string,
        'comments': comments,
        'comment_form': comment_form
    }
    return render(request, 'post_detail.html', context)

def posts_list(request):
    #queryset_list = Post.objects.all()#.order_by('-timestamp')
    #queryset_list = Post.objects.filter(draft=False).filter(publish__lte=timezone.now())  # .order_by('-timestamp')

    if request.user.is_staff or request.user.is_superuser:
        queryset_list = Post.objects.all()
    else:
        queryset_list = Post.objects.active()

    query = request.GET.get('q')
    if query:
        queryset_list = queryset_list.filter(
            Q(title__icontains=query) |
            Q(content__icontains=query) |
            Q(user__first_name__icontains=query) |
            Q(user__last_name__icontains=query)).distinct()
    paginator = Paginator(queryset_list, 3) # Show 25 contacts per page
    page = request.GET.get('page')
    try:
        queryset = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        queryset = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        queryset = paginator.page(paginator.num_pages)

    today = timezone.now().date()
    print today
    context = {
        'title':'LIST',
        'queryset': queryset,
        'today': today
    }
    return render(request, 'post_list.html', context)

@login_required(login_url='/login')
def posts_update(request, slug):
    if not request.user.is_staff or not request.user.is_superuser:
        return Http404()
    obj = get_object_or_404(Post, slug=slug)
    form = PostForm(request.POST or None, request.FILES or None, instance=obj)
    if form.is_valid():
        instance = form.save(commit=False)
        instance.save()
        messages.success(request, 'SUCCESS')
        return HttpResponseRedirect(instance.get_absolute_url())
    else:
        messages.error(request, 'ERROR')
    context = {
        'title': 'DETAIL',
        'object': obj,
        'form': form,
    }
    return render(request, 'post_create.html', context)

@login_required(login_url='/login')
def posts_delete(request, id):
    if not request.user.is_staff or not request.user.is_superuser:
        return Http404()
    obj = get_object_or_404(Post, id=id)
    obj.delete()
    messages.success(request, 'DELETED')
    return HttpResponseRedirect(obj.get_absolute_url())