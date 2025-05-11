from django.urls import path

from . import views
from .views import register_view, CustomLoginView, logout_view, home, profile_view, chat_view, teacher_students


urlpatterns = [
    path('', home, name='home'),
    path('register/', register_view, name='register'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', logout_view, name='logout'),
    path('profile/', profile_view, name='profile'),
    path('chat/', chat_view, name='chat'),
    path('teacher/students/', teacher_students, name='teacher_students'),
    path('teacher/class_groups/', views.manage_class_groups, name='manage_class_groups'),
    path('student/attendance/', views.student_attendance, name='student_attendance'),
    path('create-chat-group/', views.create_chat_group, name='create_chat_group'),
    path('about/', views.about_view, name='about'),
]

