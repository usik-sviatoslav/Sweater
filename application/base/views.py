from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from django.db.models import Count, Q
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, UpdateView

from posts.forms import CommentModalWindow
from posts.models import Post
from posts.views import like_button_view
from base.forms import RegistrationPage, LoginPage, EditUserProfilePage
from base.models import User


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


class UserProfile(ListView):

    def get_user(self):
        return get_object_or_404(
            User.objects.all().prefetch_related('subscriptions', 'subscribers'), username=self.kwargs['username']
        )

    def get_view(self):
        view_name = self.request.resolver_match.view_name
        return 'media-posts' if view_name == 'profile' else 'posts'

    def is_file(self):
        return True if self.get_view() == 'media-posts' else False

    def get_context_data(self, **kwargs):
        kwargs['user'] = self.get_user()
        kwargs['page'] = self.get_view()
        kwargs['forms'] = CommentModalWindow()
        kwargs['like_button_view'] = like_button_view(self.request, kwargs)
        return kwargs

    def get_queryset(self):
        queryset = Post.objects.filter(user__username=self.kwargs['username'])
        post_filter = (
            queryset
            .annotate(comments_count=Count('comments', filter=Q(comments__parent_comment=None)))
            .filter(is_file=self.is_file())
            .select_related('user')
            .prefetch_related('likes')
        )
        return queryset.count(), post_filter

    def get(self, request, *args, **kwargs):
        post_count, post_filter = self.get_queryset()
        context = self.get_context_data(post_count=post_count, posts=post_filter)
        return render(request, 'base/user_profile.html', context)


class UpdateUserProfile(UpdateView):
    model = User
    form_class = EditUserProfilePage
    template_name = 'base/edit_user_profile.html'

    def get_object(self, queryset=None):
        return self.request.user

    def get(self, request, *args, **kwargs):
        user = self.get_object()
        form = self.form_class(instance=user)
        return render(request, self.template_name, {'form': form})

    def form_valid(self, form):
        user = self.get_object()

        if form.cleaned_data['password']:
            user.password = make_password(form.cleaned_data['password'])

        user.save()
        login(self.request, user)
        return redirect('profile', username=user.username)


class SubscriptionListView(ListView):

    def get_queryset(self):
        if self.get_view() == 'followers':
            users = (
                User.objects.get(username=self.kwargs['username'])
                .subscribers.all().prefetch_related('subscribers')
            )
        else:
            users = (
                User.objects.get(username=self.kwargs['username'])
                .subscriptions.all().prefetch_related('subscribers')
            )
        return users

    def get_view(self):
        return self.request.resolver_match.view_name

    def get(self, *args, **kwargs):
        users = self.get_queryset()
        context = {'users': users}

        return render(self.request, 'base/followers_subscriptions.html', context)


@login_required(login_url='login')
def subscribe(request, username):
    user = get_object_or_404(User, username=username)

    if request.user != user:
        is_subscribe = True if request.resolver_match.view_name == 'subscribe' else False
        user.subscribers.add(request.user) if is_subscribe else user.subscribers.remove(request.user)

        user_subscribers = user.subscribers.all().count()
        user_subscriptions = user.subscriptions.all().count()

        return JsonResponse({
            'is_subscribe_button': is_subscribe,
            'subscribers': user_subscribers,
            'subscriptions': user_subscriptions
        })

    return redirect('profile', request.user.username)


def search(request):
    users = User.objects.all().prefetch_related('subscribers')
    context = {'users': users}
    return render(request, 'base/search.html', context)


def logout_user(request):
    logout(request)
    return redirect('home')


def custom_404_view(request, exception):
    return render(request, 'base/404.html', status=404)
