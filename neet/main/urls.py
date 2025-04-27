from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name="home"),
    path('login/', views.login, name="login"),
    path('logout/', views.logout, name="logout"),
    path('centers/', views.centers, name="centers"),
    path('operators/', views.operators, name="operators"),
    path('centers/<int:center_id>/', views.center_detail, name="center_detail"),
    
    path('api/operators/create/', views.create_operator, name="create_operator"),
    path('api/operators/update/<int:operator_id>/', views.update_operator, name="update_operator"),
    path('api/operators/delete/<int:operator_id>/', views.delete_operator, name="delete_operator"),
    path('api/centers/<int:center_id>/add-operators/', views.add_operators_to_center, name="add_operators_to_center"),
    path('api/centers/<int:center_id>/remove-operator/<int:operator_id>/', views.remove_operator_from_center, name="remove_operator_from_center"),
]
