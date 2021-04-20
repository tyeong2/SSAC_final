from django.urls import path
from . import views

urlpatterns = [
    path('', views.home),
    path('register/', views.register),
    path('login/', views.login),
    path('logout/', views.logout),
    path('list/', views.board_list),
    path('write/', views.board_write),
    path('detail/<int:pk>/', views.board_detail),
    path('detail/<int:pk>/update/', views.board_update),
    path('detail/<int:pk>/delete/', views.board_delete),
    path('guide/', views.guide),
    path('aboutus/', views.aboutus),
    path('design/', views.design),
    path('mypage/', views.mypage),
    path('mypage/update/', views.mypage_update)
]