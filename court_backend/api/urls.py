from django.urls import path
from .views import DelhiHighCourtScraper

urlpatterns = [
    path('scrape/', DelhiHighCourtScraper.as_view()),
]
