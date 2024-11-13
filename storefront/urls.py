from django.urls import path
from . import views

urlpatterns = [
    path("cart/create/<int:id>/", views.create_cart),
    path("cart/update/", views.update_cart),
    path("login/", views.customer_accesss_token_create),
    path("cart_with_selling_plan/", views.create_cart_with_selling_plan),
    path("cart_data/", views.cart_data),
]
