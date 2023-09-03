from django.urls import path
from . import views

handler404 = views.custom_404_view

urlpatterns = [
    path('register/', views.RegisterPageView.as_view(), name="register"),
    path('login/', views.LoginPageView.as_view(), name="login"),
    path('logout/', views.logout_user, name="logout"),

    path('search/', views.search, name="search"),
    path('@<str:username>/', views.user_profile, name="profile"),
    path('@<str:username>/<str:posts>/', views.user_profile, name="profile_posts"),
]
