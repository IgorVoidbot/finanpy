from django.urls import path

from categories.views import (
    CategoryCreateView,
    CategoryDeleteView,
    CategoryListView,
    CategoryUpdateView,
)

app_name = 'categories'

urlpatterns = [
    path('categorias/', CategoryListView.as_view(), name='category_list'),
    path('categorias/nova/', CategoryCreateView.as_view(), name='category_create'),
    path('categorias/<int:pk>/editar/', CategoryUpdateView.as_view(), name='category_update'),
    path('categorias/<int:pk>/excluir/', CategoryDeleteView.as_view(), name='category_delete'),
]
