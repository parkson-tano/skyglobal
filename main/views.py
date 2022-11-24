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
import datetime
import ast
amadeus = Client(
    client_id='G10V3YXxeLaBSrVDLfVj0qAGIxS1BRHA',
    client_secret='01neJa0qM0djzTma'
)

flight = []

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
            trip_type = request.POST["TripType"] 
            stops = request.POST['Stops']
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
            currency = request.POST['Currency']
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
                price = []
                data = []
                p = []
                seg = []
                if stops == '0':
                    for i in response.data:
                        if i['oneWay'] != 'false':
                            data.append(i)
                elif stops == '1':
                    for i in response.data:
                        p.append(i['itineraries'])
                        for y in p:
                            seg.append(y[0])
                        if len(y[0]['segments']) <=1:
                            data.append(i)

                elif stops == '2':
                    for i in response.data:
                        p.append(i['itineraries'])
                        for y in p:
                            seg.append(y[0])
                        if len(y[0]['segments']) <=2:
                            data.append(i)
  
                else:
                    data = response.data
                for i in data:
                    price.append(float(i['price']['grandTotal']))
                
                max_price = max(price)
                min_price = min(price)
     
                context = {
                    "data": data,
                    'origin': origin_code,
                    'destination': destination_code,
                    'depart_date':datetime.datetime.strptime(departure_date, '%Y-%m-%d'), 
                    'currency' : currency,
                    'seat': travel_class,
                    'max_price': max_price,
                    'min_price': min_price,
                    'trip_type':trip_type,
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
                price = []
                data = []
                p = []
                seg = []
        
                if stops == '0':
                    for i in response.data:
                        if i['oneWay'] != 'false':
                            data.append(i)
                elif stops == '1':
                    for i in response.data:
                        p.append(i['itineraries'])
                        for y in p:
                            seg.append(y[0])
                        if len(y[0]['segments']) <=1:
                            data.append(i)
                elif stops == '2':
                    for i in response.data:
                        p.append(i['itineraries'])
                        for y in p:
                            seg.append(y[0])
                        if len(y[0]['segments']) <=2:
                            data.append(i)
                else:
                    data = response.data
                for i in response.data:
                    price.append(float(i['price']['grandTotal']))
                
                max_price = max(price)
                min_price = min(price)
   
                context = {
                    "data": data,
                    'origin': origin_code,
                    'destination': destination_code,
                    'depart_date':datetime.datetime.strptime(departure_date, '%Y-%m-%d'), 
                    'return_date':datetime.datetime.strptime(return_date, '%Y-%m-%d'), 
                    'seat': travel_class,
                    'currency' : currency,
                     'max_price': max_price,
                    'min_price': min_price,
                    'trip_type': trip_type,
                                    }
            print(context)
            # return JsonResponse(context)
            return render(request, 'search.html', context=context)
        except ResponseError as error:
            print(error)
    else:
        return JsonResponse({"error": "Invalid request method"})

class Booking(TemplateView):
    template_name = 'flight/book.html'

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
            flight = flight.replace('\"','')
            print(flight)
            booking = amadeus.booking.flight_orders.post(flight, traveler)
            return JsonResponse(booking)
        except ResponseError as error:
            print(error)
    else:
        return JsonResponse({"error": "Invalid request method"})


def review(request):
    flightID = request.POST['flight1Id']
    flightDate = request.POST['flight1Date']
    flightSeat = request.POST['seatClass']
    flight = request.POST['flight']
    fly = flight.replace('\"', '')

    a = {
        'type': 'flight-offer', 'id': '2', 'source': 'GDS', 'instantTicketingRequired': False, 'nonHomogeneous': False, 'oneWay': False, 'lastTicketingDate': '2022-11-25', 'numberOfBookableSeats': 7, 'itineraries': [{'duration': 'PT36H15M', 'segments': [{'departure': {'iataCode': 'LGA', 'terminal': 'C', 'at': '2022-12-09T19:00:00'}, 'arrival': {'iataCode': 'YYZ', 'terminal': '3', 'at': '2022-12-09T20:40:00'}, 'carrierCode': 'WS', 'number': '1215', 'aircraft': {'code': '7M8'}, 'operating': {'carrierCode': 'WS'}, 'duration': 'PT1H40M', 'id': '93', 'numberOfStops': 0, 'blacklistedInEU': False}, {'departure': {'iataCode': 'YYZ', 'terminal': '3', 'at': '2022-12-10T06:30:00'}, 'arrival': {'iataCode': 'YYC', 'at': '2022-12-10T09:00:00'}, 'carrierCode': 'WS', 'number': '653', 'aircraft': {'code': '73H'}, 'operating': {'carrierCode': 'WS'}, 'duration': 'PT4H30M', 'id': '94', 'numberOfStops': 0, 'blacklistedInEU': False}, {'departure': {'iataCode': 'YYC', 'at': '2022-12-10T20:45:00'}, 'arrival': {'iataCode': 'LHR', 'terminal': '3', 'at': '2022-12-11T12:15:00'}, 'carrierCode': 'WS', 'number': '18', 'aircraft': {'code': '789'}, 'operating': {'carrierCode': 'WS'}, 'duration': 'PT8H30M', 'id': '95', 'numberOfStops': 0, 'blacklistedInEU': False}]}], 'price': {'currency': 'EUR', 'total': '315.13', 'base': '146.00', 'fees': [{'amount': '0.00', 'type': 'SUPPLIER'}, {'amount': '0.00', 'type': 'TICKETING'}], 'grandTotal': '315.13', 'additionalServices': [{'amount': '28.96', 'type': 'CHECKED_BAGS'}]}, 'pricingOptions': {'fareType': ['PUBLISHED'], 'includedCheckedBagsOnly': False}, 'validatingAirlineCodes': ['WS'], 'travelerPricings': [{'travelerId': '1', 'fareOption': 'STANDARD', 'travelerType': 'ADULT', 'price': {'currency': 'EUR', 'total': '315.13', 'base': '146.00'}, 'fareDetailsBySegment': [{'segmentId': '93', 'cabin': 'ECONOMY', 'fareBasis': 'LTQD0ZEK', 'brandedFare': 'ECONO', 'class': 'L', 'includedCheckedBags': {'quantity': 0}}, {'segmentId': '94', 'cabin': 'ECONOMY', 'fareBasis': 'LTQD0ZEK', 'brandedFare': 'ECONO', 'class': 'L', 'includedCheckedBags': {'quantity': 0}}, {'segmentId': '95', 'cabin': 'ECONOMY', 'fareBasis': 'LP0D0TEI', 'brandedFare': 'ECONO', 'class': 'L', 'includedCheckedBags': {'quantity': 0}}]}]
    }
    



    context = {
            'flight1':a,
            }
    # return JsonResponse(context)
    return render(request, 'flight/book.html', context=context, )     

