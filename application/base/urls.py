from django.urls import path
from . import views

handler404 = views.custom_404_view

urlpatterns = [
    path('register/', views.RegisterPageView.as_view(), name="register"),
    path('login/', views.LoginPageView.as_view(), name="login"),
    path('logout/', views.logout_user, name="logout"),

    path('search/', views.search, name="search"),
    path('@<str:username>/', views.UserProfile.as_view(), name="profile"),
    path('@<str:username>/posts/', views.UserProfile.as_view(), name="profile_posts"),
    path('@<str:username>/edit/', views.UpdateUserProfile.as_view(), name="edit_profile"),

    path('<str:username>/subscribe/', views.subscribe, name='subscribe'),
    path('<str:username>/unsubscribe/', views.subscribe, name='unsubscribe'),
    path('<str:username>/followers/', views.SubscriptionListView.as_view(), name='followers'),
    path('<str:username>/subscriptions/', views.SubscriptionListView.as_view(), name='subscriptions'),
]
