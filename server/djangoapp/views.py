from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
from .models import CarModel
from .restapis import get_dealers_from_cf, get_dealer_reviews_from_cf, post_request, get_dealer_by_id
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from datetime import datetime
import logging
import json

# Get an instance of a logger
logger = logging.getLogger(__name__)


# Create your views here.


# Create an `about` view to render a static about page
def about(request):
    return render(request, "about.html")


# Create a `contact` view to return a static contact page
def contact(request):
    return render(request, "contact.html")

# Create a `login_request` view to handle sign in request
def login_request(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['psw']
        user = authenticate(username=username,
                            password=password)
        if user is not None:
            login(request, user)
    return redirect('djangoapp:index')

# Create a `logout_request` view to handle sign out request
def logout_request(request):
    logout(request)
    return redirect('djangoapp:index')

# Create a `registration_request` view to handle sign up request
def registration_request(request):
    context = {}
    if request.method == 'GET':
        return render(request, 'djangoapp/registration.html', context)
    elif request.method == 'POST':
        username = request.POST['username']
        password = request.POST['psw']
        first_name = request.POST['firstname']
        last_name = request.POST['lastname']
        user_exist = False
        try:
            User.objects.get(username=username)
            user_exist = True
        except:
            logger.debug("{} is new user".format(username))
        if not user_exist:
            user = User.objects.create_user(username=username,
                                            first_name=first_name,
                                            last_name=last_name,
                                            password=password)
            login(request, user)
            return redirect(redirect)
        else:
            return render(request, 'djangoapp/registration.html', context)

# Update the `get_dealerships` view to render the index page with a list of dealerships
def get_dealerships(request):
    if request.method == "GET":
        context = {}
        url = "https://us-south.functions.appdomain.cloud/api/v1/web/118184fe-af96-45aa-b259-200ae71d5674/dealership-package/get-dealership"
        # Get dealers from the URL
        dealerships = get_dealers_from_cf(url)
        context["dealership_list"] = dealerships
        return render(request, 'djangoapp/index.html', context)
        # Concat all dealer's short name
        #dealer_names = ' '.join([dealer.short_name for dealer in dealerships])
        # Return a list of dealer short name
        #return HttpResponse(dealer_names)

# Create a `get_dealer_details` view to render the reviews of a dealer
# def get_dealer_details(request, dealer_id):
# ...
def get_dealer_details(request, dealer_id):
    if request.method == "GET":
        context = {}
        url = "https://us-south.functions.appdomain.cloud/api/v1/web/118184fe-af96-45aa-b259-200ae71d5674/dealership-package/get-review"
        reviews = get_dealer_reviews_from_cf(url, dealer_id)
        context["dealer_id"] = dealer_id
        context["reviews_list"] = reviews
        return render(request, 'djangoapp/dealer_details.html', context)
        #reviews_text = ' '.join([review.review + " (" + str(review.sentiment) + ")" for review in reviews])
        #return HttpResponse(reviews_text)

# Create a `add_review` view to submit a review
# def add_review(request, dealer_id):
# ...
def add_review(request, dealer_id):
    if request.user.is_authenticated:
        if request.method == "GET":
            context = {}
            url = "https://us-south.functions.appdomain.cloud/api/v1/web/118184fe-af96-45aa-b259-200ae71d5674/dealership-package/get-dealership"
            cars = CarModel.objects.filter(dealer_id=dealer_id)
            dealer = get_dealer_by_id(url, dealer_id)
            context["cars"] = cars
            context["dealer"] = dealer
            return render(request, 'djangoapp/add_review.html', context)
        elif request.method == "POST":
            url = "https://us-south.functions.appdomain.cloud/api/v1/web/118184fe-af96-45aa-b259-200ae71d5674/dealership-package/post-review"
            cars = CarModel.objects.filter(dealer_id=dealer_id)
            car = cars[int(request.POST['car'])-1]
            review = {}
            review["name"] = request.user.get_full_name()
            review["purchase_date"] = request.POST['purchasedate']
            review["dealership"] = dealer_id
            review["review"] = request.POST['content']
            review["purchase"] = request.POST['purchasecheck']
            review["car_make"] = car.car_make.name
            review["car_model"] = car.name
            review["car_year"] = car.year
            #review = {}
            #review["name"] = "Ahmed Emara"
            #review["purchase_date"] = "1/2/2023"
            #review["dealership"] = dealer_id
            #review["review"] = "This is a great car dealer"
            #review["purchase"] = True
            #review["car_make"] = "Renault"
            #review["car_model"] = "Logan"
            #review["car_year"] = 2016
            json_payload = {}
            json_payload["review"] = review
            response = post_request(url, json_payload)
            return HttpResponse(response)
