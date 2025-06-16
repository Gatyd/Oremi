from django.urls import path
from .carte_grise_extraction import CarteGriseExtractorView

urlpatterns = [
    path('api/carte-grise/extract/', CarteGriseExtractorView.as_view(), name='carte-grise-extract'),
]