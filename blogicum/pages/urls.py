from . import views
from django.urls import path


app_name = 'pages'

urlpatterns = [
    path('about.html/', views.About.as_view(), name='about'),
    path('rules.html/', views.Rules.as_view(), name='rules'),
]
