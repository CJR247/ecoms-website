from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import LogoutView




urlpatterns = [
    path('', views.store,name='store'),
    path('cart/', views.cart,name='cart'),
    path('checkout/',views.checkout, name='checkout'),
    path('update_item/',views.updateItem,name='update_item'),
    path('process_order/',views.processOrder,name='process_order'),
    path('login/',views.login_user, name='login'),
    path('logout/',views.logout_user, name='logout'),
    path('register/',views.register_user, name='register'),
    path('order_history/',views.order_history, name='order_history'),

    
   

   

    


]