from django.http.response import HttpResponse
from django.shortcuts import render
from django.http import HttpRequest
from sharespace.models import Item, Category, Sub_Category, User, UserProfile, Neighbourhood

# Create your views here.

def index (request):
    context_dict = {'boldmessage' : 'this is a try'}
    return render(request, 'sharespace/index.html', context=context_dict)
