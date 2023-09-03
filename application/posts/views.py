from io import BytesIO

from PIL import Image
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView

from .forms import NewPostPage, CommentForPostPage
from .models import Post, LikeForPost, LikeForComment, CommentForPost, CommentForComment


def home(request, username=None):
    all_posts = Post.objects.all()
    form = CommentForPostPage()
    user_posts = Post.objects.filter(user__username=username)
    show_posts = all_posts if username is None else user_posts
    context = {'posts': show_posts, 'page': 'posts', 'forms': form}

    like_button_view(request, context)
    return render(request, 'posts/post_or_comments.html', context)


def view_post(request, post_id):
    page = 'post'
    form = CommentForPostPage()
    post = get_object_or_404(Post, id=post_id)
    post_comments = CommentForPost.objects.filter(post=post_id)
    context = {'page': page, 'post': post, 'comments': post_comments, 'forms': form}

    like_button_view(request, context, post_id)
    return render(request, 'posts/post_or_comments.html', context)


def view_comment(request, post_id, comment_id):
    page = 'other_comments'
    post = get_object_or_404(Post, id=post_id)
    current_comment = get_object_or_404(CommentForPost, id=comment_id)
    other_comments = CommentForComment.objects.filter(comment_id=comment_id)

    context = {'page': page, 'post': post, 'comment': current_comment, 'other_comments': other_comments}
    like_button_view(request, context, post_id)
    return render(request, 'posts/post_or_comments.html', context)


def reply_on_post(request, post_id):
    form = CommentForPostPage(request.POST)
    if form.is_valid():
        form_instance = form.save(commit=False)
        form_instance.user = request.user
        form_instance.post_id = post_id
        form_instance.save()
        return redirect('view_post', post_id)


@login_required(login_url='login')
def like_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    like, created = LikeForPost.objects.get_or_create(user=request.user, post=post)

    if not created:
        like.delete()

    post_like_count = LikeForPost.objects.filter(post=post).count()
    post_comment_count = CommentForPost.objects.filter(post=post).count()
    profile_image = str(request.user.profile_image)

    return JsonResponse({
        'is_liked': created,
        'post_like_count': post_like_count,
        'post_comment_count': post_comment_count,
        'profile_image': profile_image
    })


@login_required(login_url='login')
def like_comment(request, post_id, comment_id):
    post = get_object_or_404(Post, id=post_id)
    like, created = LikeForComment.objects.get_or_create(user=request.user, post=post, comment_id=comment_id)

    if not created:
        like.delete()

    comment_like_count = LikeForComment.objects.filter(post=post, comment=comment_id).count()
    comment_comment_count = CommentForComment.objects.filter(post_id=post, comment_id=comment_id).count()

    return JsonResponse({
        'is_liked': created,
        'comment_like_count': comment_like_count,
        'comment_comment_count': comment_comment_count,
    })


def like_button_view(request, context, post_id=None):
    user = request.user
    if user.is_authenticated:
        if post_id:
            like_comment_by_user = {
                like.comment_id: like for like in LikeForComment.objects.filter(user=user, post=post_id)
            }
            context['like_comment_by_user'] = like_comment_by_user

        like_post_by_user = {like.post_id: like for like in LikeForPost.objects.filter(user=user)}
        context['like_post_by_user'] = like_post_by_user

    return context


class NewPostPageView(LoginRequiredMixin, ListView):
    form_class = NewPostPage
    template_name = 'posts/new_post.html'
    context_object_name = 'form'
    success_url = 'home'
    login_url = 'login'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, {self.context_object_name: self.form_class()})

    def post(self, request):
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


def image_converter(form):
    uploaded_file = Image.open(form.file)
    webp_output = BytesIO()
    uploaded_file.save(webp_output, format="webp", quality=80)
    webp_output.seek(0)
    form.file.save(f"{form.file.name.split('.')[0]}.webp", webp_output)
