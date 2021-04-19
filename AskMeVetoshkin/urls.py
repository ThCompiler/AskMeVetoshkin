"""AskMeVetoshkin URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from app import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('hot/', views.hot_questions, name="hot_question"),
    path('author/<int:current_author>/', views.author_questions, name="current_author"),
    path('tag/<str:current_tag>/', views.tag_questions, name="current_tag"),
    path('new/', views.new_questions, name="new_question"),
    path('login/', views.log_in, name="login"),
    path('signup/', views.sign_up, name="signup"),
    path('quest/<int:pk>/', views.current_question, name='current_question'),
    path('set/', views.settings, name="settings"),
    path('', views.index,  name="root")
]
