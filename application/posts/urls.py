from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name="home"),
    path('new-post/', views.NewPostPageView.as_view(), name="new_post"),
    path('reply/<int:post_id>/', views.reply_on_post, name="reply_on_post"),

    path('like-post/<int:post_id>/', views.like_post, name='like_post'),
    path('like-comment/<int:post_id>/<int:comment_id>/', views.like_comment, name='like_comment'),

    path('post/<int:post_id>/', views.view_post, name='view_post'),
    path('post/<int:post_id>/<int:comment_id>/', views.view_comment, name='view_comment'),
]
