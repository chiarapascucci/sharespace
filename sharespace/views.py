from django.forms.models import modelformset_factory
from django.http.response import HttpResponse
from django.shortcuts import render, redirect
from django.http import HttpRequest, HttpResponse
from sharespace.models import Image, Item, Category, Sub_Category, User, UserProfile, Neighbourhood, Loan
from sharespace.forms import AddItemForm, BorrowItemForm, ImageForm, UserForm, UserProfileForm
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.urls import reverse
from django.contrib.auth import authenticate, logout
from django.contrib.auth import login as auth_login
from django.views import View
from pprint import pprint as pp
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm


# Create your views here.


def index(request):
    context_dict = {'boldmessage': 'this is a try'}
    # for p in Item.objects.raw('SELECT owner FROM sharespace_item'):
    #   print(p)

    return render(request, 'sharespace/index.html', context=context_dict)


def item_list_view(request):
    return render(request)


def register_view(request):
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
            profile.set_hood(request.POST.get('user_post_code'))
            print(type(profile))
            print(profile.hood)

            if 'picture' in request.FILES:
                profile.picture = request.FILES['picture']

            profile.save()

            registered = True

        else:
            print(user_form.errors, profile_form.errors)

    else:
        user_form = UserForm()
        profile_form = UserProfileForm()

    return render(request, 'sharespace/sign_up.html',
                  context={'user_form': user_form, 'profile_form': profile_form, 'registered': registered})


def address_lookup_view(request):
    return render(request, 'sharespace/post_code_lookup.html', {})


@login_required
def add_item_view(request):
    ImageFormSet = modelformset_factory(Image, form=ImageForm, extra=3)

    if request.method == 'POST':
        add_item_form = AddItemForm(request.POST)
        formset = ImageFormSet(request.POST, request.FILES)

        # print(request.POST)

        if add_item_form.is_valid():
            print('form is valid')
            item = add_item_form.save(commit=False)
            print(item.owner)

            item.save()
            item.owner.add()
            item.save()

            for form in formset.cleaned_data:
                if form:
                    image = form['image']
                    Image.objects.create(image=image, item=item)

            return redirect(reverse('sharespace:item_page', kwargs={'item_slug': item.item_slug}))
        else:
            print('there are form errors in item form', add_item_form.errors, add_item_form.is_valid)
            print('there are form errors in image forms', formset.errors, formset.is_valid)
    else:
        add_item_form = AddItemForm()
        formset = ImageFormSet(queryset=Image.objects.none())
        return render(request, 'sharespace/add_item.html', context={'add_item_form': add_item_form, 'formset': formset})


def item_page_view(request, item_slug):
    item_page_context = {}

    try:
        item = Item.objects.get(item_slug=item_slug)
        item_page_context['item'] = item
        item_page_context['owners'] = item.owner.all()
        item_page_context['gallery'] = item.images.all()
        # print("in item view: " , item, item.owner.all())
        pp(item_page_context)
        print(item_page_context['owners'].exists())
    except Item.DoesNotExist:
        item_page_context['item'] = None

    return render(request, 'sharespace/item_page.html', context=item_page_context)


def gallery_view(request, item_slug):
    item = Item.objects.get(item_slug=item_slug)
    return render(request, 'galley.html', {"item": item})


def category_list_view(request):
    print("in cat list view")
    cat_list_context = {}
    cat_list_context['all_cat'] = Category.objects.all().order_by('name')
    print(cat_list_context['all_cat'])
    return render(request, 'sharespace/category_list.html', context=cat_list_context)


def category_page_view(request, cat_slug):
    cat = Category.objects.get(cat_slug=cat_slug)
    cat_context = {}
    cat_context['name'] = cat.name
    cat_context['all_items'] = Item.objects.filter(main_category=cat).order_by('name')

    return render(request, 'sharespace/category_page.html', context=cat_context)


def sub_cat_page_view(request):
    return render(request, 'sharespace/sub_cat.html', context={})


def about_view(request):
    print("in the about view")
    return render(request, 'sharespace/about.html', context={})


def user_profile_view(request, user_slug):
    print("in user profile view")
    user_profile_context = {}

    try:
        username = request.user.get_username()
        name = request.user.get_full_name()

        print('printing username: ', username)
        print('printin full name:', name)

        user_profile_context['username'] = username
        user_profile_context['full_name'] = name

        try:
            user_profile = UserProfile.objects.get(user_slug=user_slug)
            user_profile_context['bio'] = user_profile.bio
            user_profile_context['owned_items'] = user_profile.owned.all()
            user_profile_context['borrowing_items'] = None #need to sort this
            user_profile_context['picture'] = user_profile.picture
            print(user_profile_context)

        except UserProfile.DoesNotExist:
            print("no user profile")
    except User.DoesNotExist:
        print("no user")

    return render(request, 'sharespace/user_profile.html', context=user_profile_context)


def edit_user_view(request):
    return render(request, 'sharespace/edit_user_info.html', context={})

@login_required
def change_password_view(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, 'Your password was successfully updated!')
            return redirect(reverse('sharespace:index'))
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'sharespace/change_password.html', {
        'form': form
    })

def login(request):
    # If the request is a HTTP POST, try to pull out the relevant information.
    if request.method == 'POST':

        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(username=username, password=password)

        if user:

            if user.is_active:

                auth_login(request, user)
                return redirect(reverse('sharespace:index'))
            else:

                return HttpResponse("Your account is disabled.")
        else:

            print(f"Invalid login details: {username}, {password}")
            return HttpResponse("Invalid login details supplied.")
    else:
        return render(request, 'sharespace/login.html')


@login_required
def user_logout(request):
    logout(request)
    return redirect(reverse('sharespace:index'))


def borrow_item_view(request, item_slug):
    if request.method == 'POST':
        print("post request")

    else:
        form = BorrowItemForm()
        return render(request, 'sharespace/borrow_item.html', {'form': form})


class BorrowItemView(View):
    print("in borrow item viewp")

    @method_decorator(login_required)
    def get(self, request, item_slug):
        form = BorrowItemForm()
        return render(request, 'sharespace/borrow_item.html', {'form': form, 'item_slug': item_slug})

    @method_decorator(login_required)
    def post(self, request, item_slug):
        form = BorrowItemForm(request.POST)
        username = request.user.get_username()
        print(username)
        user = User.objects.get(username=username)

        try:
            user_p = UserProfile.objects.get(user = user)
        except UserProfile.DoesNotExist:
            print("no user here")
            return render(request, 'sharespace/index.html', {})

        try:
            item = Item.objects.get(item_slug=item_slug)
        except Item.DoesNotExist:
            print("no item retrived")
            return render(request, 'sharespace/index.html', {})

        if form.is_valid():
            # len = request.POST('len_of_loan')
            loan = Loan.objects.create(item_on_loan = item, requestor = user_p)
            print(loan)

            return redirect(reverse('sharespace:index'))
        else:
            print(form.errors)

        return render(request, 'sharespace/borrow_item.html', {'form': form})

