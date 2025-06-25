"""
URL configuration for pms project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
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
from django.urls import path
from app1 import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    # path('', views.base, name='base'),
    path('projects/', views.project_list, name='project_list'),
    path('projects/<int:pk>/', views.project_detail_view, name='project-detail'),
    # path('project/<int:pk>/update/', views.project_update_ajax, name='project-update-ajax'),
    path('projects/<int:pk>/edit/', views.edit_project, name='edit_project'),
    path('projects/<int:pk>/delete/', views.delete_project, name='project-delete'),
    path('projects/pdf/', views.generate_project_pdf, name='project-pdf'),

    path('transactions/', views.transaction_list, name='transaction_list'),
    path('add-transaction/', views.add_transaction, name='add_transaction'),
    path('transactions/<int:pk>/view/', views.view_transaction, name='view_transaction'),
    path('transactions/<int:pk>/edit/', views.edit_transaction, name='edit_transaction'),
    path('transactions/<int:pk>/delete/', views.delete_transaction, name='delete_transaction'),

    path('staff/', views.staff_list, name='staff_list'),
    path('staff/delete/<int:staff_id>/', views.delete_staff, name='delete_staff'),
    # path('view/<int:pk>/', views.view_staff, name='view_staff'),
    path('add-category/', views.add_category, name='add_category'),


    
    path('loans/', views.loan_list, name='loan_list'),
    path('loans/create/', views.create_loan, name='create_loan'),
    path('loans/update/<int:pk>/', views.update_loan, name='update_loan'),
    path('loans/delete/', views.delete_loan, name='delete_loan'),
    # urls.py
    path('loans/<int:loan_id>/', views.loan_detail, name='loan_detail'),
    # path('loans/<int:loan_id>/add_repayment/', views.add_repayment, name='add_repayment'),
    #  path('loan/<int:loan_id>/pdf/', views.generate_loan_pdf, name='loan_pdf'),
    path('loans/download-pdf/', views.download_loan_pdf, name='download_loan_pdf'),


    path('task_list', views.task_list, name='task_list'),
    path('delete/<int:pk>/', views.delete_task, name='delete_task'),
    path('view/<int:pk>/', views.view_task, name='view_task'),

    path('', views.dashboard_view, name='dashboard'),
    path('loan/<int:loan_id>/pdf/', views.loan_pdf, name='loan_pdf'),
    path('transactions_pdf/', views.transaction_pdf, name='transaction_pdf'),


    # path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    # path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),

    # path('staff/dashboard/', views.staff_dashboard, name='staff_dashboard'),
    path('admin/messages/', views.admin_messages, name='admin_messages'),
    path('staff/dashboard/', views.staff_dashboard, name='staff_dashboard'),
    # path('staff/send-message/', views.send_message_to_admin, name='send_message'),



    path('repayment/<int:repayment_id>/view/', views.repayment_detail, name='repayment_detail'),
    path('repayment/<int:repayment_id>/edit/', views.edit_repayment, name='edit_repayment'),
    path('repayment/<int:repayment_id>/delete/', views.delete_repayment, name='delete_repayment'),

    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),




    path('target/', views.target_dashboard, name='target_dashboard'),
    path('target/add/', views.add_target, name='add_target'),
    path('target/<int:pk>/edit/', views.edit_target, name='edit_target'),
    path('target/<int:pk>/delete/', views.delete_target, name='delete_target'),
    path('get-next-project-code/', views.get_next_project_code, name='get_next_project_code'),
    
    
    

    

    
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
