from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from .views import *

urlpatterns = [
    path('', index, name='index'),
    path('origin_airport_search/', origin_airport_search,
         name='origin_airport_search'),
    path('select_destination/<str:param>', select_destination,
         name="select_destination"),
    path('search_offers/', search_offers, name="search_offers"),
    path('price_offers/', price_offer, name="price_offer"),
    path('book_flight/', book_flight, name="book_flight"),
]