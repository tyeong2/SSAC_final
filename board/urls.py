from django.urls import path
from . import views

urlpatterns = [
    path('', views.home),
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('list/', views.board_list, name='board_list'),
    path('write/', views.board_write, name='board_write'),
    path('detail/<int:pk>/', views.board_detail, name='board_detail'),
    path('detail/<int:pk>/update/', views.board_update, name='board_update'),
    path('detail/<int:pk>/delete/', views.board_delete, name='board_delete'),
    path('guide/', views.guide, name='guide'),
    path('aboutus/', views.aboutus, name='aboutus'),
    path('design/', views.design, name='design'),
    path('mypage/', views.mypage, name='mypage'),
    path('mypage/update/', views.mypage_update, name='mypage_update'),
    path('comment/create/<int:board_id>/', views.comment_create_board, name='comment_create_board'),
    path('comment/modify/<int:comment_id>/', views.comment_modify_board, name='comment_modify_board'),
    path('comment/delete/<int:comment_id>/', views.comment_delete_board, name='comment_delete_board'),
    path('vote_detail/<int:board_id>/', views.vote_board_detail, name='vote_board_detail'),
    path('vote/<int:board_id>/', views.vote_board, name='vote_board'),
]
