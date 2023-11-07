from django.db import models
from base.models import User


class PostManager(models.Manager):
    pass


class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    file = models.ImageField(upload_to='posts/', null=True, blank=True, verbose_name='file')
    is_file = models.BooleanField(default=False)
    content = models.TextField(null=True, blank=True)

    likes = models.ManyToManyField(User, related_name='liked_posts', blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    objects = PostManager()


class CommentManager(models.Manager):
    pass


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField(null=True, blank=True)

    likes = models.ManyToManyField(User, related_name='liked_comments', blank=True)
    parent_comment = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    objects = CommentManager()
