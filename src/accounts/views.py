from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.contrib.auth import authenticate, get_user_model, login, logout
from .forms import UserLoginForm, UserRegisterForm

# Create your views here.
def login_view(request):
    title = 'Login'
    next = request.GET.get('next')
    form = UserLoginForm(request.POST or None)
    if form.is_valid():
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password')
        user = authenticate(username=username, password=password)
        login(request, user)
        if next:
            return redirect(next)
        return redirect('/')
    context_data = {
        'form': form,
        'title': title
    }
    return render(request, 'form.html', context_data)

def register_view(request):
    title = 'Register'
    next = request.GET.get('next')
    form = UserRegisterForm(request.POST or None)
    if form.is_valid():
        user = form.save(commit=False)
        password = form.cleaned_data.get('password')
        user.set_password(password=password)
        user.save()
        new_user = authenticate(username=user.username, password=user.password)
        login(request, new_user)
        if next:
            return redirect(next)
        return redirect('/')
    context_data = {
        'form': form,
        'title': title
    }
    return render(request, 'form.html', context_data)

def logout_view(request):
    logout(request)
    return redirect('/login')