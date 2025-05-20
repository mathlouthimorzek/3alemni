from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('dashboard/teacher/', views.teacher_dashboard, name='teacher_dashboard'),
    path('dashboard/student/', views.student_dashboard, name='student_dashboard'),
    path('dashboard/admin/', views.admin_dashboard, name='admin_dashboard'),
    path('add_course/', views.add_course, name='add_course'),
    path('add_assignment/', views.add_assignment, name='add_assignment'),
    path('download_course/<int:course_id>/', views.download_course, name='download_course'),
    path('submit_assignment/<int:assignment_id>/', views.submit_assignment, name='submit_assignment'),
    path('download_assignment/<int:assignment_id>/', views.download_assignment, name='download_assignment'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('grade_submission/<int:submission_id>/', views.grade_submission, name='grade_submission'),
    path('courses/', views.course_list, name='course_list'),
    path('logout/', views.custom_logout, name='logout'),
    path('espace/<int:espace_id>/', views.espace_detail, name='espace_detail'),
    path('update-dashboard-time/', views.update_dashboard_time, name='update_dashboard_time'),  # New endpoint
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
