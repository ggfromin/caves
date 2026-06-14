from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('marketplace/', views.marketplace, name='marketplace'),
    path('marketplace/item/<int:item_id>/', views.item_detail, name='item_detail'),
    path('marketplace/buy/<int:item_id>/', views.buy_item, name='buy_item'),
    path('marketplace/comment/<int:item_id>/', views.add_comment, name='add_comment'),
    path('cities/', views.cities, name='cities'),
    path('cities/<int:city_id>/', views.city_detail, name='city_detail'),
    path('buy-server-access/', views.buy_server_access, name='buy_server_access'),  
]