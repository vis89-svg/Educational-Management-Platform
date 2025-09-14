from django.urls import path

from .views import (
    TeacherResgister,
    LoginView,
    ProfileView,
    EditProfileView,
    DeleteProfileView,
    AllTeachersView
)

urlpatterns = [
    # ✅ Teacher Registration
    path('teachers/register/', TeacherResgister.as_view(), name='teacher_register'),

    # ✅ Teacher Login
    path('teachers/login/', LoginView.as_view(), name='teacher_login'),

    # ✅ Teacher Profile (logged-in user)
    path('teachers/profile/', ProfileView.as_view(), name='teacher_profile'),

    # ✅ Edit Teacher Profile (PUT/PATCH)
    path('teachers/profile/<int:pk>/edit/', EditProfileView.as_view(), name='edit_teacher_profile'),

    # ✅ Delete Teacher Profile (DELETE)
    path('teachers/profile/<int:pk>/delete/', DeleteProfileView.as_view(), name='delete_teacher_profile'),

    # ✅ Admin – View all teachers
    path('teachers/all/', AllTeachersView.as_view(), name='all_teachers'),
]
