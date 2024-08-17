from django.urls import path,include
from rest_framework.routers import DefaultRouter
from . import views

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('token', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh', TokenRefreshView.as_view(), name='token_refresh'), 
    path('auth/register/', views.AuthView.as_view(), name='register'),
    path('auth/logout/', views.AuthView.as_view(), name='logout'),
    path('clothes/', views.ClothesListView.as_view(), name='clothes'),
    path('saved/', views.SavedViewSet.as_view({'get': 'list', 'post': 'create'}), name='saved_list'),
    path('saved/unsave/<int:pk>', views.SavedViewSet.as_view({'delete': 'unsave'}), name='unsave'),
    path('users/', views.UserViewSet.as_view({'get': 'list'}), name='users_list'),
    path('users/<int:pk>', views.UserViewSet.as_view({'get': 'retrieve'}), name='user_detail'),
    path('report/', views.BugReportView.as_view(), name='bug_report'),
    path('change/password/',views.ChangePasswordView.as_view(),name='change_password'),
    path('history/',views.HistoryView.as_view(),name='history_list'),
    path('feedback/',views.FeedBackViewSet.as_view({'get': 'list', 'post': 'create'}),name='feedback'),
    path('category/',views.CategoriesViewSet.as_view({'get': 'list', 'post': 'create'}),name='cateogries'),
    path('category/<int:pk>',views.CategoriesViewSet.as_view({'get': 'retrieve'}),name='cateory_details'),
    path('category/clothes/<int:pk>',views.CategoriesViewSet.as_view({'get': 'clothes_by_category'}),name='clothes_by_category'),
    path('download/<int:pk>',views.DownloadView.as_view(),name='download')
]  

