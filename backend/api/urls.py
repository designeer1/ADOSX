from django.urls import path
from . import views

urlpatterns = [
    path('compare/', views.compare_files, name='compare_files'),
    path('results/', views.get_results, name='get_results'),
    path('reasons/', views.get_reasons, name='get_reasons'),
    path('clear/', views.clear_data, name='clear_data'),
]