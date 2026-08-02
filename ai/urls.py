from django.urls import path

from .views import AnalysisDetailView, AnalysisListView, GenerateAnalysisView

app_name = 'ai'

urlpatterns = [
    path('analises/', AnalysisListView.as_view(), name='analysis_list'),
    path('analises/gerar/', GenerateAnalysisView.as_view(), name='generate'),
    path('analises/<int:pk>/', AnalysisDetailView.as_view(), name='analysis_detail'),
]
