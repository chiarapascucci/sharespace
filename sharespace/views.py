from django.http.response import HttpResponse
from django.shortcuts import render
from django.http import HttpRequest
from sharespace.models import Item, Category, Sub_Category, User, UserProfile, Neighbourhood
from sharespace.forms import AddItemForm, UserForm, UserProfileForm
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

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

            profile = profile_form.save(commit=False)
            profile.user = user
            print(type(profile))
            profile.save(user_post_code = request.POST.get('user_post_code'))

            registered = True

            if 'picture' in request.FILES:
                profile.picture = request.FILES['picture']
        
        else:print(user_form.errors, profile_form.errors)
    
    else:
        user_form = UserForm()
        profile_form = UserProfileForm()
    
    return render(request, 'sharespace/sign_up.html', context = {'user_form': user_form, 'profile_form': profile_form, 'registered' : registered})

            
@login_required
def add_item(request):

    if request.method == 'POST':
        add_item_form = AddItemForm(request.POST)

        if add_item_form.is_valid():
            item = add_item_form.save()
            item.save()
        else:
            print(add_item_form.errors)
    else:
        add_item_form = AddItemForm()

    return render(request, 'sharespace/add_item.html', context = {'add_item_form' : add_item_form})


def item_page(request):

    return render(request, 'sharespace/item_page.html', context = {})


def category_list(request):

    return render(request, 'sharespace/category_list.html', context = {})

def category_page(request):

    return render(request, 'sharespace/category_page.html', context = {})

def sub_cat_page(request):

    return render(request, 'sharespace/sub_cat.html', context = {})

def about(request):

    return render(request, 'sharespce/about.html', context={})

def user_profile(request):
    return render(request, 'user_profile.html', context= {})

def edit_user(request):
    return render(request, 'sharespace/edit_user_info.html', context = {})

def login(request):

    return render(request, 'sharespace/login.html', context= {})