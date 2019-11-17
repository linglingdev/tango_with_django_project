

from django.urls import path
from rango import views

app_name = 'rango'
urlpatterns = [
    path(r'', views.index, name="index"),
    path(r'about/', views.about, name="about"),
    path(r'category/<slug:category_name_slug>/', views.show_category, name="show_category"),
    path(r'add_category/', views.add_category, name='add_category'),
    path(r'category/<slug:category_name_slug>/add_page/', views.add_page, name='add_page'),
    # path(r'register/', views.register, name='register'),
    # path(r'login/', views.user_login, name='login'),
    path(r'restricted/', views.restricted, name='restricted'),
    path(r'search/', views.search, name='search'),
    path(r'goto/', views.track_url, name='goto'),
    path(r'register_profile/', views.register_profile, name='register_profile'),
    path(r'profile/<slug:username>/', views.profile, name='profile'),
    path(r'like/', views.like_category, name='like_category'),
    path(r'test/', views.test_html, name='test_html'),
    path(r'suggest/', views.suggest_category, name='suggest_category'),
    path(r'add/', views.auto_add_page, name='auto_add_page')
    # path(r'logout/', views.user_logout, name='logout')
]

