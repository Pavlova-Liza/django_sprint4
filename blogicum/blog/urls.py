from . import views
from django.urls import path

app_name = 'blog'

urlpatterns = [
    path('', views.index, name='index'),
    path('category/<slug:category_slug>/', views.category_posts,
         name='category_posts'),

    path('posts/<int:post_id>/', views.post_detail,
         name='post_detail'),
    path('posts/create/', views.create_post, name='create_post'),
    path('posts/<int:post_id>/edit/', views.post_update,
         name='edit_post'),
    path('posts/<int:post_id>/delete/', views.post_delete,
         name='delete_post'),

    path('profile/<str:username>/', views.profile, name='profile'),
    path('posts/edit_profile/', views.edit_profile,
         name='edit_profile'),

    path('posts/<int:post_id>/comment/', views.add_comment, name='add_comment'),
    path('posts/<int:post_id>/delete_comment/<int:comment_id>/',
         views.comment_delete, name='delete_comment'),
    path('posts/<int:post_id>/edit_comment/<int:comment_id>/',
         views.comment_update, name='edit_comment'),
]
