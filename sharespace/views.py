from django.http.response import HttpResponse
from django.shortcuts import render
from django.http import HttpRequest
from sharespace.models import Item, Category, Sub_Category, User, UserProfile, Neighbourhood
from sharespace.forms import UserForm, UserProfileForm

# Create your views here.

def index (request):
    context_dict = {'boldmessage' : 'this is a try'}
    return render(request, 'sharespace/index.html', context=context_dict)


def register(request):
    registered = False

    if request.method == 'POST':
        user_form = UserForm(request.POST)
        profile_form = UserProfileForm(request.POST)

        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            user.set_password(user.password)
            user.save()

            profile = profile_form.save(commit=False, user_post_code = request.POST.get('post_code'))
            profile.user = user

            registered = True

            if 'picture' in request.FILES:
                profile.picture = request.FILES['picture']
        
        else:print(user_form.errors, profile_form.errors)
    
    else:
        user_form = UserForm()
        profile_form = UserProfileForm()
    
    return render(request, 'sharespace/sign_up.html', context = {'user_form': user_form, 'profile_form': profile_form, 'registered' : registered})

            
