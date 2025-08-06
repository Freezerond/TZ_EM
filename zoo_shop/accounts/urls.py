from django.urls import path
from .views import *

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('delete-account/', DeleteUserView.as_view(), name='delete-account'),
    path('user/profile/', UserUpdateView.as_view(), name='user-update'),


    path('products/', ProductListView.as_view()),
    path('order/', OrderCreateView.as_view()),
    path('manage/products/', ProductManageView.as_view()),
    path('user/delete/<int:user_id>', AdminManageUsersView.as_view()),
    path('users/', UserListView.as_view(), name='user-list'),
    path('promote/', PromoteToManagerView.as_view(), name='promote-to-manager'),
]