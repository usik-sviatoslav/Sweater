from django.urls import path
from . import views

urlpatterns = [
    path('', views.PostListView.as_view(), name="home"),

    path('post/create/', views.NewPostPageView.as_view(), name="new_post"),
    path('post/<int:post_id>/', views.PostDetailView.as_view(), name='view_post'),
    path('post/<int:post_id>/update/', views.EditPostPageView.as_view(), name='edit_post'),
    path('post/<int:post_id>/delete/', views.remove_post, name='remove_post'),

    path('post/<int:post_id>/reply/', views.reply_on_post, name="reply_on_post"),
    path('post/<int:post_id>/report/', views.report_on_post, name='report_on_post'),

    path('like-button/<int:content_id>/<str:content_type>', views.like_button, name='like_button'),

    path('comment/<int:post_id>/<int:comment_id>/', views.CommentListView.as_view(), name='view_comment'),
    path('comment/<int:post_id>/<int:comment_id>/reply/', views.reply_on_comment, name="reply_on_comment"),

]
