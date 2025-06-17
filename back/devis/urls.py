from django.urls import path
from .carte_grise_extraction import CarteGriseExtractorView
from .views import (
    DevisListCreateView, DevisDetailView, DevisByClientView, devis_stats
)

urlpatterns = [
    # API Carte Grise
    path('api/carte-grise/extract/', CarteGriseExtractorView.as_view(), name='carte-grise-extract'),
    
    # API Devis
    path('api/devis/', DevisListCreateView.as_view(), name='devis-list-create'),
    path('api/devis/<int:pk>/', DevisDetailView.as_view(), name='devis-detail'),
    path('api/devis/client/<str:npi>/', DevisByClientView.as_view(), name='devis-by-client'),
    path('api/devis/stats/', devis_stats, name='devis-stats'),
]