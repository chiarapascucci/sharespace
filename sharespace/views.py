from django.db.models import Subquery, Q
from django.forms.models import modelformset_factory
from django.http.response import HttpResponse
from django.shortcuts import render, redirect
from django.http import HttpRequest, HttpResponse
from sharespace.models import Image, Item, Category, Sub_Category, User, UserProfile, Neighbourhood, Loan, Address, \
    LoanCompleteNotification
from sharespace.forms import AddItemForm, BorrowItemForm, ImageForm, UserForm, UserProfileForm, AddItemFormWithAddress
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
from datetime import datetime, date, time, timedelta
import time
from django.http import JsonResponse

# ------- FUNCTION BASED VIEWS (alph sorted) -------
# --- most views check if there is a logged in user (server side)

def about_view(request):
    print("in the about view")
    return render(request, 'sharespace/about.html', context={})


@login_required
def add_item_view(request):
    ImageFormSet = modelformset_factory(Image, form=ImageForm, extra=3)

#   handling POST type request (forms is used to create item entity in DB)
    if request.method == 'POST':

        # extracting relevant data and handling manually
        # name and description of item
        name = request.POST['name']
        print(name)
        description = request.POST['description']
        print(description)

        # main category and secondary category
        main_cat_name = request.POST['main_category']
        main_cat = Category.objects.get(name=main_cat_name)
        print(type(main_cat))
        sec_category_name = request.POST['sec_category']
        sec_category = Sub_Category.objects.get(name=sec_category_name)
        print(type(sec_category))

        # max loan length
        max_loan_len = request.POST['max_loan_len']

        # creating/getting address from data provided on address location
        item_address = create_address(request)

        # creating item instance in DB
        item_added = Item.objects.create(name=name, description=description, main_category = main_cat,
                                         sec_category=sec_category, location=item_address,
                                         max_loan_len = max_loan_len)

        # handling setting owners for the item

        # getting user name of user submitting the request
        username = request.user.get_username()
        print(username)
        # getting user profile from username (CHANGE THIS TO HELPER FUNCTION TO MANAGE IF EXCEPTION IS RAISED)
        us = User.objects.get(username=username)
        up = UserProfile.objects.get(user=us)
        print("up: ", up)
        item_added.owner.add(up)
        item_added.save()

        # adding possible extra owners added when submitting form
        owners = find_owners(request)
        if not owners:
            for o in owners:
                item_added.add(o)
                item_added.save()

        # handling any images attached to the item form
        formset = ImageFormSet(request.POST, request.FILES)

        if formset.is_valid():
            for form in formset.cleaned_data:
                if form:
                    image = form['image']
                    Image.objects.create(image=image, item=item_added)
        else:
            print("errors in image form")

        return redirect(reverse('sharespace:item_page', kwargs={'item_slug': item_added.item_slug}))

# handling GET type requests
    else:
        item_context = {'formset': ImageFormSet(queryset=Image.objects.none())}
        up_dict = extract_us_up(request)
        if up_dict:
            user_profile = up_dict['up']
            user = up_dict['us']
            item_context['user_profile'] = user_profile
            hood = user_profile.hood
            item_context['hood'] = hood.nh_post_code
            print(hood)
            poss_coowners = UserProfile.objects.filter(hood=hood).exclude(user=user)
            item_context['owners']=poss_coowners
            print(poss_coowners)

        item_context['categories'] = Category.objects.all()

        return render(request, 'sharespace/add_item.html', context= item_context)


def address_lookup_view(request):
    return render(request, 'sharespace/post_code_lookup.html', {})


@login_required()
def borrow_item_view(request, item_slug):
    if request.method == 'POST':
        print("post request")

    else:
        form = BorrowItemForm()
        return render(request, 'sharespace/borrow_item.html', {'form': form})


def category_list_view(request):
    print("in cat list view")
    cat_list_context = {}
    cat_list_context['all_cat'] = Category.objects.all().order_by('name')
    #print(cat_list_context['all_cat'])
    return render(request, 'sharespace/category_list.html', context=cat_list_context)


def category_page_view(request, cat_slug):
    print("in category page view, trying to extract users")
    up_cont = extract_us_up(request)
    cat = Category.objects.get(cat_slug=cat_slug)
    cat_context = {'name': cat.name}
    #if dict is empty
    if not up_cont:
        print("dict is empty")
        cat_context['all_items'] = Item.objects.filter(main_category=cat).order_by('name')
    else:
        up_post_code = up_cont['up'].user_post_code
        print(up_post_code)
        hood = Neighbourhood.objects.get(nh_post_code = up_post_code)
        hood_list = Address.objects.filter(adr_hood = hood)
        items_available_in_hood = Item.objects.filter(location__in = Subquery(hood_list.values('pk'))).filter(main_category = cat)
        print(items_available_in_hood)
        cat_context['all_items'] = items_available_in_hood


    return render(request, 'sharespace/category_page.html', context=cat_context)


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


@login_required()
def edit_user_view(request):
    return render(request, 'sharespace/edit_user_info.html', context={})


def gallery_view(request, item_slug):
    item = Item.objects.get(item_slug=item_slug)
    return render(request, 'galley.html', {"item": item})


def hood_page_view(request):
    hood_context = {}
    return render(request, 'sharespace/hood_page.html', context=hood_context)


# index view
def index(request):
    up_dict = extract_us_up(request)
    context_dict = {}
    if up_dict:
        context_dict['up'] = up_dict['up']

    else:
        pass

    return render(request, 'sharespace/index.html', context=context_dict)


# item list view - not sure where this is used???
def item_list_view(request):
    return render(request)


def item_page_view(request, item_slug):
    item_page_context = {}

    try:
        item = Item.objects.get(item_slug=item_slug)
        print("item information: \n name: ", item.name, "available: ", item.available)
        item_page_context['item'] = item
        item_page_context['owners'] = item.owner.all()
        item_page_context['gallery'] = item.images.all()

    except Item.DoesNotExist:
        item_page_context['item'] = None

    up_dict = extract_us_up(request)
    if up_dict:
        item_page_context['up'] = up_dict['up']

    return render(request, 'sharespace/item_page.html', context=item_page_context)


# ajax view
def load_sub_cat_view(request):
    cat = request.GET.get('main_category_id')
    print(cat)
    sub_cat_list = Sub_Category.objects.filter(parent = cat)
    return render(request, 'sharespace/sub_cat_dropdown_list.html', {'list' : sub_cat_list})


# ajax view
def load_user_profile_view(request):
    username = request.GET.get('username')
    print(username)
    try:
        user = User.objects.get(username=username)
        try:
            user_profile = UserProfile.objects.get(user = user)
            user_url = reverse('sharespace:user_profile', kwargs={'user_slug': user_profile.user_slug})
            print(type(user_url))
            add_item_url = reverse('sharespace:add_item')
            return JsonResponse({'user_url' : user_url , 'add_item_url' : add_item_url})
        except UserProfile.DoesNotExist:

            profile_url = reverse('sharespace:complete_profile')
            return JsonResponse({ 'profile_url' : profile_url})
    except User.DoesNotExist:
        print("user does not exist - views 253")
        return JsonResponse({})


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


# register view. if post request data from user and user profile registration form is used to create entities in DB
# if get forms are rendered. registered flag : T/F
def register_view(request):
    registered = False
    register_user_context = {'registered': registered}
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

    register_user_context['user_form'] = user_form
    register_user_context['profile_form'] = profile_form

    return render(request, 'sharespace/sign_up.html', context=register_user_context)


class CompleteProfileView(View):
    @method_decorator(login_required)
    def get(self, request):
        profile_form = UserProfileForm()
        profile_dict = extract_us_up(request)
        if profile_dict['up'] is not None:
            print("you already have a profile") # need to handle this
            return redirect(reverse('sharespace:index'))
        else:
            return render(request, 'sharespace/complete_profile.html', {'form' : profile_form})

    def post(self, request):
        profile_dict = extract_us_up(request)
        if profile_dict['up'] is not None:
            print("you already have a profile") # need to handle this
            return redirect(reverse('sharespace:index'))
        else:
            profile_form = UserProfileForm(request.POST)
            if profile_form.is_valid():
                profile = profile_form.save(commit=False)
                profile.user = profile_dict['us']
                profile.set_hood(request.POST.get('user_post_code'))
                print(type(profile))
                print(profile.hood)

                if 'picture' in request.FILES:
                    profile.picture = request.FILES['picture']

                profile.save()

                return redirect(reverse('sharespace:user_profile', kwargs={'user_slug': profile.user_slug}))
            else:
                print(profile_form.errors)
                return render(request, 'sharespace/complete_profile.html', {})


def sub_cat_page_view(request):
    return render(request, 'sharespace/sub_cat.html', context={})


@login_required
def user_logout(request):
    logout(request)
    return redirect(reverse('sharespace:index'))


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
            print("user is borrowing: ", user_profile.curr_no_of_items, "\n user can borrow mad:",
                  user_profile.max_no_of_items, "you can still borrow? ", user_profile.can_borrow)
            user_profile_context['bio'] = user_profile.bio
            user_profile_context['post_code'] = user_profile.user_post_code
            user_profile_context['owned_items'] = user_profile.owned.all()
            notif_list = get_user_notification(user_profile)
            if notif_list:
                user_profile_context['notifications'] = notif_list
            try:

                user_profile_context['borrowing_items'] = user_profile.loans.all()

                #print("this is the name of the item on loan ", user_profile.loans.all().item_on_loan.name)
            except Loan.DoesNotExist:
                print("no item on loan exception")
                user_profile_context['borrowing_items'] = None

            user_profile_context['picture'] = user_profile.picture
            print(user_profile_context)

        except UserProfile.DoesNotExist:
            print("no user profile")
    except User.DoesNotExist:
        print("no user")

    return render(request, 'sharespace/user_profile.html', context=user_profile_context)


# ---------- CLASS BASED VIEWS ------------


class BorrowItemView(View):
    print("in borrow item viewp")

    @method_decorator(login_required)
    def get(self, request, item_slug):

        try:
            item = Item.objects.get(item_slug=item_slug)
            print(item.max_loan_len)
            max_len = item.max_loan_len
            choices = []
            for i in range(1, max_len + 1):
                choices.append(i)
        except Item.DoesNotExist:
            print("no item here (views/360")
        return render(request, 'sharespace/borrow_item.html',
                      {'item': item, 'item_slug': item_slug, 'choices': choices})

    @method_decorator(login_required)
    def post(self, request, item_slug):
        print("printing post request : ", request.POST)

        user_dict = extract_us_up(request)
        item_slug = request.POST['item_slug']
        len_of_loan = int(request.POST['len_of_loan'])
        out_date = datetime.now()

        if user_dict:
            up = user_dict['up']
            user_slug = up.user_slug

        else:
            print("no user found")
            return render(request, 'sharespace/index.html', {})

        try:
            item = Item.objects.get(item_slug=item_slug)
            loan = Loan.objects.create(requestor=up, item_on_loan=item, len_of_loan=len_of_loan, out_date=out_date)
            print(loan)
            loan_slug = loan.loan_slug
            loan.apply_loan(len_of_loan)

        except Item.DoesNotExist:
            print("no item retrived")
            return render(request, 'sharespace/index.html', {})

        return redirect(reverse('sharespace:loan_page', kwargs={'loan_slug': loan_slug}))


class LoanView(View):
    @method_decorator(login_required)
    def get(self, request, loan_slug):
        loan = Loan.objects.get(loan_slug=loan_slug)
        btn_flag = False
        if loan.status == 'act':
            btn_flag=True
        loan_context = {'loan': loan, 'btn_flag' : btn_flag }

        return render(request, 'sharespace/loan_page.html', context=loan_context)

    def post(self, request):
        pass


class MarkItemAsReturnedPendingApproval(View):
    @method_decorator(login_required)
    def get(self, request):
        print("request received for marking item as returned")

        loan_slug = request.GET['loan_slug']
        print("loan slug in view: ", loan_slug)

        try:
            print("trying loan")
            loan = Loan.objects.get(loan_slug=loan_slug)
            loan.mark_as_complete_by_borrower()
        except Loan.DoesNotExist:
            print("no loan")

        except ValueError:
            return HttpResponse(-1)

        return HttpResponse(loan.status)


class SearchView (View):

    def get(self, request):
        search_context = {}

        search = request.GET['search_input'].strip().lower()
        search_context['search'] = search
        search_context['category'] = Category.objects.filter(Q(name__contains=search) | Q(description__contains=search))
        search_context['sub_category'] = Sub_Category.objects.filter(Q(name__contains=search) | Q(description__contains=search))
        search_context['items'] = Item.objects.filter(Q(name__contains=search) | Q(description__contains=search))

        up_dict = extract_us_up(request)
        if up_dict:
            post_code = up_dict['up'].hood.nh_post_code
            search_context['items'].filter(item_post_code=post_code)

        return render(request, 'sharespace/search_result_page.html', context=search_context)

    def post(self, request):
        search_context = {}
        return render(request, 'sharespace/search_result_page.html', context=search_context)


class LoanCompleteNotificationView (View):
    @method_decorator(login_required)
    def get(self, request, notification_slug):
        form = None

        notif = LoanCompleteNotification.objects.get(notification_slug = notification_slug)
        print(notif)
        sender = notif.sender
        receiver = notif.receiver
        title = notif.title
        body = notif.body
        context = {
            'form' : form,
            'notification' : notif,
            'sender': sender,
            'receiver' : receiver,
            'title' : title,
            'body': body,
            'notification_slug':notification_slug,
        }
        return render(request, 'sharespace/notification_page.html', context=context)

    @method_decorator(login_required)
    def post(self, request, notification_slug):
        print(request)
        input_value = request.POST['action-desired-selection']
        if input_value == 'returned-ok':
            message = """ Thank you for confirming that your item was returned correctly
                            and thank you for sharing something with your neighbours
                            hold on tight while we redirect you"""
            context={'message' : message}
            up_dict = extract_us_up(request)
            if up_dict['up'] is not None:
                context['profile_slug']= up_dict['up'].user_slug

            return render(request, 'sharespace/waiting_page.html', context)
        else:
            #will need to redirect to complaint / dispute form
            return redirect(reverse('sharespace:index'))



# ---------------- HELPER FUNCTIONS --------------


def get_user_notification(up):
    try:
        notification_list = up.received_notifications.all()
        print("got notication list, print:")
        for n in notification_list:
            print("something? Anything??!!")
            print("not: ", n)
        return notification_list

    except LoanCompleteNotification.DoesNotExist:
        print("no notification to pass")
        return []


def find_owners(request):
    list = []
    for key in request:
        if request[key] == 'on':
            print(key)
            us = User.objects.get(username = key)
            up = UserProfile.objects.get(user=us)
            list.append(up)
            print(up)

    return list


def create_address(adr_dict):
    hood = Neighbourhood.objects.get_or_create(nh_post_code = adr_dict.POST['postcode'])[0]
    item_adr = Address.objects.get_or_create(address_line_1 = adr_dict.POST['adr_line_1'],
                                             address_line_2 = adr_dict.POST['adr_line_2'],
                                             address_line_3 = adr_dict.POST['adr_line_3'],
                                             address_line_4 = adr_dict.POST['adr_line_4'],
                                             city = adr_dict.POST['city'],
                                             locality = adr_dict.POST['locality'],
                                             county = adr_dict.POST['county'],
                                             adr_hood = hood)[0]

    return item_adr


def extract_us_up (request):
    if request.user.is_anonymous:
        print("anonymous user")
        return {}
    else:
        try:
            username = request.user.get_username()
            us = User.objects.get(username = username)

            try:
                up = UserProfile.objects.get(user = us)
                return {'us': us, 'up' : up}

            except UserProfile.DoesNotExist:
                print("no user profile here (views/200")
                return {'us' : us, 'up' : None}

        except User.DoesNotExist:
            print("no user here (views/200")
            return {}



























