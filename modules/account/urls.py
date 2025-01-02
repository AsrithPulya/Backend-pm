from django.urls import path
from .views import *
urlpatterns = [
    path('register/', RegisterUser.as_view(), name='registeruser'),
    path('login/', LoginUser.as_view(), name='loginuser'),
    path('reporting-managers/', ReportingManagerListView.as_view(), name='reporting-manager-list'),
    path('users/<int:user_id>/', UserDetailView.as_view(), name='user-detail'),
    # Api for reset password and forgot password
    path('forgot-password/', ForgotPasswordView.as_view(), name='forgot_password'),
    path('reset-password/', ResetPasswordView.as_view(), name='reset_password'),
    path('users/all/', UserView.as_view(), name='all_users'),
    path('new-hires/', NewHiresView.as_view(), name='new-hires'),

    path('users/update_role/', UserView.as_view(), name='update_role'), #testing for updating role
    path('users/update-manager/', ChangeManagerView.as_view(), name='update-manager'),

]
