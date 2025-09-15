"""
URL configuration for myproject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from myapp.views import landing_page

urlpatterns = [
    # Landing page at root
    path("", landing_page, name="landing"),

    # Admin
    path("admin/", admin.site.urls),

    # Apps with their own prefixes
    path("students/", include("myapp.urls")),      # students app
    path("teachers/", include("teachers.urls")),  # teachers app
    path("exams/", include("Exam.urls")),         # exams app
    path("courses/", include("cources.urls")),    # courses app
    path("results/", include("results.urls")),    # results app
    path("attendance/", include("attendence.urls")),  # attendance app
    path("payment/", include("payment.urls")),    # payment app
]

