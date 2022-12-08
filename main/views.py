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
                if len(price) > 0:
                    max_price = max(price)
                    min_price = min(price)
                else:
                    max_price = None
                    min_price = None
     
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
                
                if len(price) > 0:
                    max_price = max(price)
                    min_price = min(price)
                else:
                    max_price = None
                    min_price = None
   
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
            first_name = req.POST['passenger1FName']
            last_name = req.POST['passenger1LName']
            traveler = {'first':first_name, 'last':last_name}
            flight = req.POST['flight']
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
    destination = request.POST['destination']
    origin = request.POST['origin']
    flight = ast.literal_eval(request.POST['flight'])

    duration = ''
    depart_time = ''
    depart_date = ''
    arrive_time = ''
    arrive_date = ''
    depart_code = ''
    arrive_code = ''
    carrier_code = ''
    aircraft_code = ''
    base_price = ''
    total_price = ''
    total_price = flight['price']['total']
    base_price = flight['price']['base']
    fee = float(total_price) - float(base_price)
    fee = round(fee, 2)
    for data in flight["itineraries"]:
        duration = data['duration'][2:]
        if len(data["segments"]) == 1:
            depart_time = data["segments"][0]['departure']['at'][11:16]
            depart_date = data["segments"][0]['departure']['at'][:10]
            arrive_time = data["segments"][0]['arrival']['at'][11:16]
            arrive_date = data["segments"][0]['arrival']['at'][:10]
            depart_code = data["segments"][0]['departure']['iataCode']
            arrive_code = data["segments"][0]['arrival']['iataCode']
            carrier_code = data["segments"][0]["carrierCode"]
            aircraft_code = data["segments"][0]["aircraft"]['code']

        else:
            depart_time = data["segments"][0]['departure']['at'][11:16]
            depart_date = data["segments"][0]['departure']['at'][:10]
            depart_code = data["segments"][0]['departure']['iataCode']
            carrier_code = data["segments"][0]["carrierCode"]
            aircraft_code = data["segments"][0]["aircraft"]['code']
            arrive_time = data["segments"][len(
                data["segments"])-1]['arrival']['at'][11:16]
            arrive_date = data["segments"][len(
                data["segments"])-1]['arrival']['at'][:10]
            arrive_code = data["segments"][len(
                data["segments"])-1]['arrival']['iataCode']

    context = {
            'flight1':flight,
        "duration": duration,
        "depart_time": depart_time,
        "depart_date": datetime.datetime.strptime(depart_date, '%Y-%m-%d'),
        "arrive_time": arrive_time,
        "arrive_date": datetime.datetime.strptime(arrive_date, '%Y-%m-%d'),
        "depart_code":depart_code,
        "arrive_code":arrive_code,
        "carrier_code":carrier_code,
        "aircraft_code":aircraft_code,
        'destination':destination,
        'origin':origin,
        'total_price':  total_price,
        'base_price': base_price,
        'fee': fee,
        'seat': flightSeat.capitalize(),
            }
    # return JsonResponse(context)
    print(context)
    return render(request, 'flight/book.html', context=context, )     

