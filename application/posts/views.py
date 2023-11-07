from io import BytesIO

from PIL import Image
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Q
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, UpdateView, CreateView

from posts.forms import NewPostPage, CommentModalWindow, EditPostPage
from posts.models import Post, Comment


class PostListView(ListView):

    def get_queryset(self, user_authenticated=False):
        queryset = Post.objects.all()

        if user_authenticated is not False:
            user_subscriptions = self.request.user.subscriptions.all()
            queryset = queryset.filter(user__in=user_subscriptions)

        posts = (
            queryset
            .annotate(comments_count=Count('comments', filter=Q(comments__parent_comment=None)))
            .select_related('user')
            .prefetch_related('likes', 'user__subscribers')
            .order_by('-created_at')
        )

        return posts

    def get_context_data(self, **kwargs):
        kwargs['page'] = 'posts'
        kwargs['forms'] = CommentModalWindow()
        kwargs['like_button_view'] = like_button_view(self.request, kwargs)
        return kwargs

    def get(self, request, *args, **kwargs):
        user_authenticated = self.request.user.is_authenticated
        posts = self.get_queryset(user_authenticated)
        context = self.get_context_data(posts=posts)

        return render(request, 'posts/post_or_comments.html', context)


class PostDetailView(DetailView):

    def get_queryset(self):
        post = get_object_or_404(
            Post.objects
            .annotate(comments_count=Count('comments', filter=Q(comments__parent_comment=None)))
            .select_related('user').prefetch_related('likes'), pk=self.kwargs['post_id']
        )

        comments = (
            Comment.objects
            .filter(post=self.kwargs['post_id'], parent_comment=None)
            .order_by('-created_at')
            .select_related('user')
            .prefetch_related('likes', 'replies')
        )

        return post, comments

    def get_context_data(self, **kwargs):
        kwargs['page'] = 'post'
        kwargs['forms'] = CommentModalWindow()
        like_button_view(self.request, kwargs, self.kwargs['post_id'])
        return kwargs

    def get(self, request, *args, **kwargs):
        post, comments = self.get_queryset()
        context = self.get_context_data(post=post, comments=comments)

        return render(request, 'posts/post_or_comments.html', context)


class NewPostPageView(LoginRequiredMixin, CreateView):
    form_class = NewPostPage
    template_name = 'posts/new_post.html'
    context_object_name = 'form'
    success_url = 'home'
    login_url = 'login'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, {self.context_object_name: self.form_class()})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST, request.FILES)
        if form.is_valid():
            form_instance = form.save(commit=False)
            form_instance.user = request.user

            if form_instance.file:
                image_converter(form_instance)
                form_instance.is_file = True

            form_instance.save()
            return redirect(self.success_url)
        else:
            return render(request, self.template_name, {self.context_object_name: form})


class EditPostPageView(LoginRequiredMixin, UpdateView):
    form_class = EditPostPage
    template_name = 'posts/edit_post.html'
    context_object_name = 'form'
    success_url = 'view_post'
    login_url = 'login'

    def get(self, request, *args, **kwargs):
        post = Post.objects.get(id=kwargs['post_id'])

        if request.user == post.user:
            initial_data = {'content': post.content}
            form = EditPostPage(initial=initial_data)
            return render(request, self.template_name, {self.context_object_name: form})
        return redirect('home')

    def post(self, request, *args, **kwargs):
        post = Post.objects.get(id=kwargs['post_id'])
        form = self.form_class(request.POST, request.FILES)

        if form.is_valid():
            post.content = form.cleaned_data['content']
            post.save()
            return redirect(self.success_url, kwargs['post_id'])
        else:
            return render(request, self.template_name, {self.context_object_name: form})


class CommentListView(ListView):

    def get_queryset(self):
        post = get_object_or_404(Post, id=self.kwargs['post_id'])
        current_comment = get_object_or_404(Comment.objects.filter(id=self.kwargs['comment_id']).select_related('user'))
        parent_comments = (
            Comment.objects
            .filter(parent_comment=self.kwargs['comment_id'])
            .select_related('user').order_by('created_at')
        )
        return post, current_comment, parent_comments

    def get_context_data(self, **kwargs):
        kwargs['page'] = 'other_comments'
        kwargs['forms'] = CommentModalWindow()
        kwargs['like_button_view'] = like_button_view(self.request, kwargs, self.kwargs['post_id'])
        return kwargs

    def get(self, *args, **kwargs):
        post, current_comment, parent_comments = self.get_queryset()
        context = self.get_context_data(post=post, comment=current_comment, parent_comments=parent_comments)
        return render(self.request, 'posts/post_or_comments.html', context)


def remove_post(request, post_id):
    post = Post.objects.get(id=post_id)

    if request.user == post.user:
        post.delete()

    return redirect('home')


def reply_on_post(request, post_id):
    form = CommentModalWindow(request.POST)
    if form.is_valid():
        form_instance = form.save(commit=False)
        form_instance.user = request.user
        form_instance.post_id = post_id

        form_instance.save()
        return redirect('view_post', post_id)


def report_on_post(request, post_id):
    pass


def reply_on_comment(request, post_id, comment_id):
    form = CommentModalWindow(request.POST)
    if form.is_valid():
        form_instance = form.save(commit=False)
        form_instance.user = request.user
        form_instance.post_id = post_id

        parent_comment = get_object_or_404(Comment, pk=comment_id)
        form_instance.parent_comment = parent_comment

        form_instance.save()
        return redirect('view_post', post_id)


@login_required(login_url='login')
def like_button(request, content_id, content_type):
    content = get_object_or_404(Post if content_type == 'post' else Comment, id=content_id)

    comments_count = Comment.objects.filter(post=content_id, parent_comment=None).count() \
        if content_type == 'post' else content.replies.count()

    user = request.user
    exists = content.likes.filter(id=user.id).exists()
    content.likes.remove(user) if exists else content.likes.add(user)
    created = False if exists else True

    profile_image = str(request.user.profile_image)

    return JsonResponse({
        'is_liked': created,
        'likes_count': content.likes.count(),
        'comments_count': comments_count,
        'profile_image': profile_image
    })


def like_button_view(request, context, post_id=None):
    user = request.user
    if user.is_authenticated:
        if post_id:
            like_comment_by_user = {like.id: like for like in user.liked_comments.filter(post_id=post_id)}
            context['like_comment_by_user'] = like_comment_by_user

        like_post_by_user = {like.id: like for like in user.liked_posts.all()}
        context['like_post_by_user'] = like_post_by_user

    return context


def image_converter(form):
    uploaded_file = Image.open(form.file)
    webp_output = BytesIO()
    uploaded_file.save(webp_output, format="webp", quality=80)
    webp_output.seek(0)
    form.file.save(f"{form.file.name.split('.')[0]}.webp", webp_output)
