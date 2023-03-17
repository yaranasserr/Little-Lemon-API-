from django.urls import path
from . import views
from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [
    path('', views.CategoriesView.as_view()),
    path('api/categories', views.CategoriesView.as_view()),
    path('api/menu-items/', views.MenuItemsView.as_view()),
    path('api/menu-items/<int:pk>/', views.SingleMenuItemView.as_view()),
    path('api/manager-view', views.ManagerView.as_view()),
    path('api/groups/manager/users/', views.ManagersView.as_view()),
    path('api/cart', views.CartView.as_view()),
    path('api/cart/menu-items/', views.CartView.as_view()),
    path('api/cart/<int:id>/', views.CartView.as_view()),
    path('api/cart/orders/', views.OrderView.as_view()),
    path('api/orders', views.OrderView.as_view()),
    path('api/orders/<int:id>/', views.OrderItemView.as_view()),
]