from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='root_path'),
    path('create/', views.create_product, name="create_product"),
    path('delete/<int:id>/', views.delete_product, name="delete_product"),
    path('api/create/', views.CreateProduct.as_view()),
    path('update/<int:id>/', views.update_product, name="update_product"),
    path('api/update/<int:id>/', views.UpdateProduct.as_view(), name="update_product"),

    path('create/collection/', views.create_collection, name="create collection"),
    path('create/draft_order/', views.create_draft_orders),

    path("create/selling_plan/", views.create_sellng_plan),
    path("list/selling_plan/", views.list_selling_plans),
    path("remove_product_from_selling_plan/", views.selling_plan_remove_product),

    path("selling_plan_group_data/", views.selling_plan_group_data),
    path("remove_variant_from_selling_plan/", views.remove_variant_from_selling_plan),
]
