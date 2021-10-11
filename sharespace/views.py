from django.http.response import HttpResponse
from django.shortcuts import render
from django.http import HttpRequest

# Create your views here.

def index (request):
    context_dict = {'boldmessage' : 'this is a try'}
    return render(request, 'sharespace/index.html', context=context_dict)
