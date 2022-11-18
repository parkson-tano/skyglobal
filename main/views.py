from django.shortcuts import render
from django.conf import settings
from django.conf.urls.static import static
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from amadeus import Client, ResponseError, Location
import amadeus
from django.contrib import messages
from django.http import HttpResponse
from django.views.generic import (CreateView, DetailView, FormView, ListView,
                                  TemplateView, View)

amadeus = Client(
    client_id='G10V3YXxeLaBSrVDLfVj0qAGIxS1BRHA',
    client_secret='01neJa0qM0djzTma'
)


def is_ajax(request):
    return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'


def origin_airport_search(request):
    if is_ajax(request=request):
        try:
            data = amadeus.reference_data.locations.get(
                keyword=request.GET.get('term', None), subType=Location.ANY).data
        except ResponseError as error:
            messages.add_message(request, messages.ERROR, error)
    return HttpResponse(get_city_airport_list(data), 'application/json')


def get_city_airport_list(data):
    result = []
    for i, val in enumerate(data):
        result.append(data[i]['iataCode']+', '+data[i]['name'])
    result = list(dict.fromkeys(result))
    return json.dumps(result)


def index(request):
    return render(request, 'index.html')


def select_destination(req, param):
    if req.method == "GET":
        try:
            print(param)
            response = amadeus.reference_data.locations.get(
                keyword=param, subType=Location.ANY)
            context = {"data": response.data}
            return JsonResponse(context)
        except ResponseError as error:
            print(error)
    else:
        return JsonResponse({"error": "Invalid request method"})


def search_offers(request):
    if request.method == "POST":
        try:
            origin_code = request.POST["Origin"]
            destination_code = request.POST["Destination"]
            departure_date = request.POST["Departuredate"]  
            return_date = ''  
            if "Returndate" in request.POST:
                return_date = request.POST["Returndate"]
            if request.POST['Adults'] == '0':
                adults = 1
            else:
                adults = request.POST['Adults']
            children = request.POST['Children']
            infant_seat = request.POST['Infant_0']
            travel_class = request.POST['Travelclass']
            if return_date == '':
                response = amadeus.shopping.flight_offers_search.get(
                    originLocationCode=origin_code[:3],
                    destinationLocationCode=destination_code[:3],
                    departureDate=departure_date,
                    adults=adults,
                    children=children,
                    infants=infant_seat,
                    travelClass=travel_class,
                )
                context = {
                    "data": response.data,
                    'origin': origin_code,
                    'destination': destination_code
                }
            else:
                response = amadeus.shopping.flight_offers_search.get(
                    originLocationCode=origin_code[:3],
                    destinationLocationCode=destination_code[:3],
                    departureDate=departure_date,
                    returnDate = return_date,
                    adults=adults,
                    children=children,
                    infants=infant_seat,
                    travelClass=travel_class,
                )
                context = {
                    "data": response.data,
                    'origin': origin_code,
                    'destination': destination_code
                }
            print(context)
            # return JsonResponse(context)
            return render(request, 'search.html', context=context)
        except ResponseError as error:
            print(error)
    else:
        return JsonResponse({"error": "Invalid request method"})


@csrf_exempt
def price_offer(req):
    if req.method == "POST":
        try:
            data = json.loads(req.body)
            flight = data.get("flight")
            response = amadeus.shopping.flight_offers.pricing.post(flight)
            return JsonResponse(response.data)
        except ResponseError as error:
            print(error)
    else:
        return JsonResponse({"error": "Invalid request method"})


@csrf_exempt
def book_flight(req):
    if req.method == "POST":
        try:
            flight = req.POST['flight']
            traveler = req.POST['traveler']
            booking = amadeus.booking.flight_orders.post(flight, traveler)
            return JsonResponse(booking)
        except ResponseError as error:
            print(error)
    else:
        return JsonResponse({"error": "Invalid request method"})
