from django.urls import path
from .views import RegisterUser, LoginUser, ReportingManagerListView, UserDetailView

urlpatterns = [
    path('register/', RegisterUser.as_view(), name='registeruser'),
    path('login/', LoginUser.as_view(), name='loginuser'),
    path('reporting-managers/', ReportingManagerListView.as_view(), name='reporting-manager-list'),
    path('users/<int:user_id>/', UserDetailView.as_view(), name='user-detail'),

]
