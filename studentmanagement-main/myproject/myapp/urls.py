from django.urls import path
from .views import (
    StudentRegistrationView,
    LoginAPIView,
    LogoutView,
    ProfileAPIView,
    EditProfileAPIView,
    DeleteStudentAPIView,
    AdminProfileAPIView,
    ForgotPasswordView,
)

urlpatterns = [
    
    path('register/', StudentRegistrationView.as_view(), name='student_register'),


    path('login/', LoginAPIView.as_view(), name='login'),

    
    path('profile/', ProfileAPIView.as_view(), name='profile'),

    
    path('profile/<int:pk>/edit/', EditProfileAPIView.as_view(), name='edit_profile'),

    
    path('profile/<int:pk>/delete/', DeleteStudentAPIView.as_view(), name='delete_profile'),

    
    path('admin-profile/', AdminProfileAPIView.as_view(), name='admin_profile'),

    path('forgot-password/', ForgotPasswordView.as_view(), name='forgot_password'),

    path("logout/", LogoutView.as_view(), name="logout"),

]
