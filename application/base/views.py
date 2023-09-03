from django.contrib.auth import login, authenticate, logout
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView

from posts.forms import CommentForPostPage
from posts.models import Post
from posts.views import like_button_view
from .forms import RegistrationPage, LoginPage
from .models import User


def logout_user(request):
    logout(request)
    return redirect('home')


class LoginPageView(ListView):
    form_class = LoginPage
    template_name = 'base/login_register_page.html'
    context_object_name = 'form'
    success_url = 'home'

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect(self.success_url)
        return render(request, self.template_name, {self.context_object_name: self.form_class(), 'page': 'login'})

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            email = request.POST.get('email').lower()
            password = request.POST.get('password')
            user = authenticate(request, email=email, password=password)

            if user is not None:
                login(request, user)
                return redirect(self.success_url if not request.GET else request.GET.get('next'))
        else:
            return render(request, self.template_name, {self.context_object_name: form, 'page': 'login'})


class RegisterPageView(ListView):
    form_class = RegistrationPage
    template_name = 'base/login_register_page.html'
    context_object_name = 'form'
    success_url = 'home'

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect(self.success_url)
        return render(request, self.template_name, {self.context_object_name: self.form_class()})

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.email.split('@')[0]
            user.save()
            login(request, user)
            return redirect(self.success_url)
        else:
            return render(request, self.template_name, {self.context_object_name: form})


def user_profile(request, username, posts=None):
    form = CommentForPostPage()
    user = get_object_or_404(User, username=username)
    page = 'media-posts' if posts is None else 'posts'
    true_false = True if page == 'media-posts' else False

    post = Post.objects.filter(user__username=username, is_file=true_false)
    context = {'user': user, 'posts': post, 'page': page, 'forms': form}
    like_button_view(request, context)
    return render(request, 'base/user_profile.html', context)


def search(request):
    users = User.objects.all()
    context = {'users': users}
    return render(request, 'base/search.html', context)


def custom_404_view(request, exception):
    return render(request, 'base/404.html', status=404)
