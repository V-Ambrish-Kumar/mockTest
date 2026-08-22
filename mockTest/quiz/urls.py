from django.urls import path
from . import views

urlpatterns = [
    # Test taking routes (These were missing!)
    path('', views.test_list, name='test_list'),
    path('<int:test_id>/start/', views.start_test, name='start_test'),
    path('attempt/<int:attempt_id>/', views.take_test, name='take_test'),
    path('ajax/save_answer/', views.save_answer, name='save_answer'),
    path('attempt/<int:attempt_id>/finish/', views.finish_test, name='finish_test'),
    
    # Results and Dashboard
    path('attempt/<int:attempt_id>/result/', views.test_result, name='test_result'),
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Authentication
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
]