from django.urls import path
from django.contrib.auth import views as auth_views
from users import views

app_name = 'users'

urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('sell/', views.SellPhoneView.as_view(), name='sell'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('head-admin/', views.HeadAdminDashboardView.as_view(), name='head_dashboard'),
    path('head-admin/add-staff/', views.AddStaffView.as_view(), name='add_staff'),
    path('user/<int:pk>/manage/', views.AdminUserManageView.as_view(), name='user_manage'),
]
