from django.contrib import admin
from .models import Post, LikeForPost, LikeForComment, CommentForPost, CommentForComment

admin.site.register(Post)
admin.site.register(LikeForPost)
admin.site.register(LikeForComment)
admin.site.register(CommentForPost)
admin.site.register(CommentForComment)
