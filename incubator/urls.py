from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Super Admin
    path('super-admin/add-admin/', views.add_admin, name='add_admin'),
    path('super-admin/users/<int:user_id>/delete/', views.delete_user, name='delete_user'),
    
    # Admin / Startup Management
    path('startups/<int:startup_id>/delete/', views.delete_startup, name='delete_startup'),
    path('startups/add/', views.add_startup, name='add_startup'),
    path('startups/<int:startup_id>/edit/', views.edit_startup, name='edit_startup'),
    path('startups/<int:startup_id>/', views.view_startup, name='view_startup'),
    path('startups/<int:startup_id>/add-member/', views.add_member, name='add_member'),
    path('startups/<int:startup_id>/add-milestone/', views.add_milestone, name='add_milestone'),
    path('startups/<int:startup_id>/members/<int:member_id>/delete/', views.delete_member, name='delete_member'),
    
    # Progress & Milestones
    path('startups/<int:startup_id>/submit-report/', views.submit_progress, name='submit_progress'),
    path('startups/<int:startup_id>/milestones/<int:milestone_id>/', views.view_milestone, name='view_milestone'),
    path('startups/<int:startup_id>/milestones/<int:milestone_id>/status/', views.update_milestone_status, name='update_milestone_status'),
    path('deliverables/<int:deliverable_id>/attach_admin/', views.attach_admin_file, name='attach_admin_file'),
    path('deliverables/<int:deliverable_id>/attach_incubatee/', views.attach_incubatee_file, name='attach_incubatee_file'),
]
