import pytz
from django.db.models import Subquery, Q
from django.forms.models import modelformset_factory
from django.http.response import HttpResponse
from django.shortcuts import render, redirect
from django.http import HttpRequest, HttpResponse
from django.template.defaultfilters import slugify
from django.views.generic import FormView

from sharespace.form_validation import validate_borrowing_form, validate_add_item_form
from sharespace.models import Image, Item, Category, Sub_Category, CustomUser, UserProfile, Neighbourhood, Loan, \
    Address, PurchaseProposal, Notification, CommentToProposal
from sharespace.forms import AddItemForm, ImageForm, UserForm, UserProfileForm, \
    SubmitReportForm, EditUserProfileBasicForm, SubmitPurchaseProposalForm
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
from django.http import JsonResponse

from sharespace.text_data import get_filler_paragraph
from sharespace.utils import get_booking_calendar_for_item_for_month, extract_us_up

utc = pytz.UTC


# ------- FUNCTION BASED VIEWS (alph sorted) -------
# --- most views check if there is a logged in user (server side)

def about_view(request):
    print("in the about view")
    fill = get_filler_paragraph()
    return render(request, 'sharespace/about.html', context={'fill': fill})


def info_view(request):
    print("in faq page")
    fill = get_filler_paragraph()
    return render(request, 'sharespace/information.html', context={'fill': fill})




class AddItemView(View):
    @method_decorator(login_required)
    def get(self, request):
        ImageFormSet = modelformset_factory(Image, form=ImageForm, extra=3)
        item_context = {'formset': ImageFormSet(queryset=Image.objects.none())}
        up_dict = extract_us_up(request)
        if up_dict['up'] is not None:
            user_profile = up_dict['up']
            user = up_dict['us']
            item_context['user_profile'] = user_profile
            hood = user_profile.hood
            item_context['hood'] = hood.nh_post_code
            print(hood)
            poss_coowners = UserProfile.objects.filter(hood=hood).exclude(user=user)
            item_context['owners'] = poss_coowners
            print(poss_coowners)

        item_context['categories'] = Category.objects.all()

        return render(request, 'sharespace/add_item.html', context=item_context)

    @method_decorator(login_required)
    def post(self, request):
        ImageFormSet = modelformset_factory(Image, form=ImageForm, extra=3)
        dict_form = process_add_item_form(request)
        if not dict_form['form_valid']:
            return HttpResponse(f"data entered in form is not correct: {dict_form['msg']} please try again")
        else:
            item_added = Item.objects.create(name=dict_form['name'], description=dict_form['description'],
                                             main_category=dict_form['main_cat'],
                                             sec_category=dict_form['sec_cat'],
                                             location=dict_form['address'],
                                             guardian=dict_form['guardian'],
                                             max_loan_len=dict_form['max_loan_len'])
            for o in dict_form['owners']:
                item_added.owner.add(o)
            item_added.save()

        formset = ImageFormSet(request.POST, request.FILES)

        if formset.is_valid():
            for form in formset.cleaned_data:
                if form:
                    image = form['image']
                    Image.objects.create(image=image, item=item_added)
        else:
            print("errors in image form")

        return redirect(reverse('sharespace:item_page', kwargs={'item_slug': item_added.item_slug}))



def ajax_cancel_booking(request):
    up_dict = extract_us_up(request)
    if up_dict['up'] is not None:
        redirect_url = reverse('sharespace:user_profile', kwargs={'user_slug': up_dict['up'].user_slug})
    else:
        redirect_url = reverse('sharespace:index')
    if request.method == 'POST':
        print(request.POST)
        print("views - 130 - log: ajax request to delete a future loan")
        loan_slug = request.POST['loan_slug']

        try:
            loan = Loan.objects.get(loan_slug=loan_slug)
            loan.delete()
            return JsonResponse({'loan_deleted': True, 'msg': "your booking has been deleted", 'redirect_url': redirect_url})
        except Loan.DoesNotExist:
            return JsonResponse({'loan_deleted': False, 'msg':"no booking found", 'redirect_url': redirect_url})
    else:
        return JsonResponse({'loan_deleted': False, 'msg': "wrong request type", 'redirect_url': redirect_url})


def ajax_delete_item(request, item_slug):
    if request.method == 'POST':
        print("views - 130 - log : printing post request for item deletion")
        print(request.POST)

        item = Item.objects.get(item_slug=item_slug)
        owner_set = item.owner.all()
        up = extract_us_up(request)['up']
        if len(owner_set) <= 1:
            item_status = item.check_curr_on_loan_status()
            if item_status['available']:
                item.delete()
                up.max_no_of_items -= 1
                up.save()
                return JsonResponse({'item_deleted': True, 'msg': "this item was removed from our records"})
            else:
                if item_status['due_date'] is None:
                    return JsonResponse({'item_deleted': False, 'msg': "there is a pending loan on this item, please "
                                                                       "check if you have any unactioned "
                                                                       "notifications"})

        else:
            item.owner.remove(user_slug=up.user_slug)
            up.max_no_of_items -= 1
            up.save()
            print("item deleted - multiple owners so only removing ownership for specified user")
        return JsonResponse({'item_deleted': True, 'msg': "we have removed you as an owner of this item. Our records "
                                                          "show that there are multiple owner for this item, "
                                                          "so the item was retained"})
    else:
        print("wrong request type")
        return JsonResponse({'item_deleted': False, 'msg': "something went wrong, please try again (wrong request type"})


class AccountDeletionView(View):
    @method_decorator(login_required)
    def get(self, request, user_slug):
        context = {}
        try:
            up = UserProfile.objects.get(user_slug=user_slug)
            items_owned = up.owned.all()
            items_list = []
            if items_owned.exists():
                for item in items_owned:
                    if len(item.owner.all()) <= 1:
                        pass
                    else:
                        if not item.guardian == up:
                            pass
                        else:
                            items_list.append(item)
                            context['item_list'] = items_list

            context['up'] = up

        except UserProfile.DoesNotExist:
            return HttpResponse("something went wrong - no profile retrieved")
        return render(request, 'sharespace/delete_account.html', context=context)

    @method_decorator(login_required)
    def post(self, request, user_slug):
        pp(request.POST)
        return HttpResponse("your account deletion request has been received. You'll get a confirmation email when the request has been processed")

def address_lookup_view(request):
    return render(request, 'sharespace/post_code_lookup.html', {})


def category_list_view(request):
    print("in cat list view")
    cat_list_context = {}
    cat_list_context['all_cat'] = Category.objects.all().order_by('name')
    # print(cat_list_context['all_cat'])
    return render(request, 'sharespace/category_list.html', context=cat_list_context)


def category_page_view(request, cat_slug):
    print("in category page view, trying to extract users")
    cat = Category.objects.get(cat_slug=cat_slug)
    cat_context = {'name': cat.name}
    sub_cat_list = Sub_Category.objects.filter(parent=cat).all()
    sub_cat_dict = {}

    up_dict = extract_us_up(request)
    print(up_dict)
    if up_dict['up'] is None:
        for sc in sub_cat_list:
            item_list = Item.objects.filter(sec_category=sc).all()
            sub_cat_dict[sc.name] = list(item_list)
    else:
        up = up_dict['up']
        for sc in sub_cat_list:
            item_list = Item.objects.filter(sec_category=sc).filter(location__adr_hood=up.hood)
            sub_cat_dict[sc.name] = list(item_list)

    pp(sub_cat_dict)
    cat_context['sub_cats'] = sub_cat_dict

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
        if not request.user.is_anonymous:

            up_dict = extract_us_up(request)
            if not up_dict['up'] is None:
                item_page_context['up'] = up_dict['up']
                flags = up_dict['up'].can_borrow_check()
                item_page_context['notif_flag'] = flags['unactioned_notif']
                item_page_context['max_item_flag'] = flags['max_no_of_items']

                if item.owner.filter(user_slug=up_dict['up'].user_slug).exists():
                    item_page_context['owner_flag'] = True

    except Item.DoesNotExist:
        item_page_context['item'] = None

    return render(request, 'sharespace/item_page.html', context=item_page_context)


# ajax view
def load_sub_cat_view(request):
    print("ajax request for sub cat")
    cat = request.GET.get('main_category_id')
    print(cat)
    sub_cat_qset = Sub_Category.objects.filter(parent=cat).all()
    sub_cat_list = list(sub_cat_qset)
    print(type(sub_cat_list))
    print(sub_cat_list)
    return render(request, 'sharespace/sub_cat_dropdown_list.html', context = {'list': sub_cat_list})


# ajax view
def load_user_profile_view(request):
    username = request.GET.get('username')
    print(username)
    try:
        user = CustomUser.objects.get(username=username)
        try:
            user_profile = UserProfile.objects.get(user=user)
            profile_url = reverse('sharespace:user_profile', kwargs={'user_slug': user_profile.user_slug})

            add_item_url = reverse('sharespace:add_item')
            pic_path = str(user_profile.picture)
            pic_path = "/media/" + pic_path
            print(type(pic_path), "---", pic_path, "--- type of user url: ", type(profile_url))


        except UserProfile.DoesNotExist:

            profile_url = reverse('sharespace:complete_profile')
            pic_path = "/media/profile_images/default_profile_image.png"

        return JsonResponse({'user_url': profile_url, 'img_path': pic_path})
    except CustomUser.DoesNotExist:
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
            print("you already have a profile")  # need to handle this
            return redirect(reverse('sharespace:index'))
        else:
            return render(request, 'sharespace/complete_profile.html', {'form': profile_form})

    def post(self, request):
        profile_dict = extract_us_up(request)
        if profile_dict['up'] is not None:
            print("you already have a profile")  # need to handle this
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

# need to convert this to a class based view
def user_profile_view(request, user_slug):
    print("in user profile view")

    user_profile_context = {}

    try:
        username = request.user.get_username()
        name = request.user.get_full_name()

        print(request.GET)

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
            user_profile_context['owned_items'] = user_profile.owned.all()[:5]
            user_profile_context['slug'] = user_profile.user_slug
            notif_list = get_user_notification(user_profile)[:10]
            user_profile_context['subscriptions'] = user_profile.interested.all()[:10]

            if notif_list:
                user_profile_context['notifications'] = notif_list
            try:
                loan_list = user_profile.loans.exclude(status='com')

                user_profile_context['borrowing_items'] = loan_list
            except Loan.DoesNotExist:
                print("no item on loan exception")
                user_profile_context['borrowing_items'] = None

            try:
                proposal_submitted = user_profile.proposals.filter(proposal_active=True)[:10]
                user_profile_context['proposals'] = proposal_submitted
            except PurchaseProposal.DoesNotExist:
                print("no props for this user")



            user_profile_context['picture'] = user_profile.picture
            print(user_profile_context)

        except UserProfile.DoesNotExist:
            print("no user profile")
    except CustomUser.DoesNotExist:
        print("no user")

    return render(request, 'sharespace/user_profile.html', context=user_profile_context)


@login_required
def edit_profile(request, user_slug):
    form = EditUserProfileBasicForm()
    if request.method == 'POST':
        print("in edit profile view, post request")
        print(request.POST)
        form = EditUserProfileBasicForm(request.POST, request.FILES,
                                        instance=UserProfile.objects.get(user_slug=user_slug))
        if form.is_valid():
            form.save(commit=True)
            return redirect(reverse('sharespace:user_profile', kwargs={'user_slug': user_slug}))
        else:
            print(form.errors)
        return redirect(reverse('sharespace:user_profile', kwargs={'user_slug': user_slug}))
    else:
        form = EditUserProfileBasicForm(instance=UserProfile.objects.get(user_slug=user_slug))
        context_dict = {}
        context_dict['form'] = form
        return render(request, ('sharespace/edit_user_info.html'), context=context_dict)


def your_items_list_view(request, user_slug):
    up = UserProfile.objects.get(user_slug=user_slug)
    item_list = up.owned.all()
    context = {'owned_items': item_list}
    return render(request, 'sharespace/owned_items_list.html', context=context)


# ---------- CLASS BASED VIEWS ------------
class EditItemView(View):
    @method_decorator(login_required)
    def get(self, request, item_slug):
        ImageFormSet = modelformset_factory(Image, form=ImageForm, extra=3)
        try:
            item = Item.objects.get(item_slug=item_slug)
            up = extract_us_up(request)['up']
            if not item.owner.filter(user_slug=up.user_slug).exists():
                return HttpResponse("you do not have permission to edit this item")
            context = {
                'categories': Category.objects.all(),
                'item': item,
                'name': item.name,
                'description': item.description,
                'main_cat': item.main_category,
                'sec_cat': item.sec_category,
                'max_len_loan': item.max_loan_len,
                'imgs': Image.objects.filter(item_id=item.item_id).all(),
                'formset_two': ImageFormSet(queryset=Image.objects.none())
            }

        except Item.DoesNotExist:
            print("view - 470 - log: no item found")
            return HttpResponse("no item found")
        return render(request, 'sharespace/edit_item_info.html', context=context)

    @method_decorator(login_required)
    def post(self, request, item_slug):
        print(request.POST)
        return render(request, 'sharespace/edit_item_info.html', context={})


class BorrowItemView(View):
    print("in borrow item viewp")

    @method_decorator(login_required)
    def get(self, request, item_slug):
        month = datetime.today().month
        year = datetime.today().year
        item = Item.objects.get(item_slug=item_slug)
        cal_list = [get_booking_calendar_for_item_for_month(item, month, year)]
        for i in range(1, 3):
            month += 1
            if month > 12:
                month = 1
                year += 1

            cal_list.append(get_booking_calendar_for_item_for_month(item, month, year))

        context = {'item_slug': item_slug, 'cal_list': cal_list, 'item': item}

        return render(request, 'sharespace/borrow_item.html', context=context)

    @method_decorator(login_required)
    def post(self, request, item_slug):
        print("wrong place for post request")
        return HttpResponse("took a wrong turn?")


def ajax_borrow_item_view(request):
    response = 'wrong request type, user not found, or no item found'
    if request.method == 'GET':
        return HttpResponse(response)
    else:
        print("views - 520 - log : printing request received (ajax) ", request.POST)
        due_date = request.POST['date_in']
        out_date = request.POST['date_out']
        item_slug = request.POST['item_slug']
        user_dict = extract_us_up(request)
        if user_dict:
            up = user_dict['up']
            user_slug = up.user_slug

        else:
            print("no user found")
            return HttpResponse(response)

        try:
            item = Item.objects.get(item_slug=item_slug)
            form_is_valid = validate_borrowing_form(item, up, out_date, due_date)
            if form_is_valid['form_valid']:
                due_date = f"{due_date}-19:00"
                due_date = datetime.strptime(due_date, "%Y-%m-%d-%H:%M").replace(tzinfo=utc)
                out_date = datetime.strptime(out_date, "%Y-%m-%d").replace(tzinfo=utc)
                print(f"views - 500 - log: printing requested out date: {out_date} - and due date: {due_date}")
                loan = Loan.objects.create(requestor=up, item_on_loan=item, due_date=due_date, out_date=out_date)
                print("views - 500 - log : printing loan - ", loan)
                return HttpResponse("loan created")
            else:
                print(
                    f"views - 500 - log: borrow item form did no pass validation form valid: {form_is_valid['form_valid']} -- message: {form_is_valid['msg']}")
                return HttpResponse(form_is_valid['msg'])

        except Item.DoesNotExist:
            print("no item retrieved")
            return HttpResponse(response)


class LoanView(View):
    @method_decorator(login_required)
    def get(self, request, loan_slug):

        loan = Loan.objects.get(loan_slug=loan_slug)
        del_flag = False
        up_flag = False
        return_flag = False
        fut_flag = False
        status_dict = loan.get_full_status()
        print(status_dict)
        if status_dict['status'] == 'fut':
            del_flag = True
        elif status_dict['status'] == 'act':
            return_flag = True
        elif status_dict['status'] == 'pen':
            if status_dict['picked_up']:
                pass
            else:
                del_flag = True
                up_flag = True
        else:
            pass
        loan_context = {'loan': loan, 'del_flag': del_flag, 'return_flag': return_flag, 'fut_flag': fut_flag}

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


class SearchView(View):

    def get(self, request):
        search_context = {}

        search = request.GET['search_input'].strip().lower()
        if search == "" or search == " ":
            return render(request, 'sharespace/search_result_page.html', {})
        print("in views - 700 - log : search term = ", search)
        search_context['search'] = search
        search_context['category'] = Category.objects.filter(Q(name__contains=search) | Q(description__contains=search))
        search_context['sub_category'] = Sub_Category.objects.filter(
            Q(name__contains=search) | Q(description__contains=search))
        search_context['items'] = Item.objects.filter(Q(name__contains=search) | Q(description__contains=search))

        up_dict = extract_us_up(request)
        print("views - 700 - log : up dict :", up_dict)
        if not up_dict['up'] is None:
            post_code = up_dict['up'].hood.nh_post_code
            search_context['items'].filter(item_post_code=post_code)

        if search_context['category'].exists() or search_context['sub_category'].exists() or search_context['items'].exists():
            search_context['results'] = True

        print(search_context)
        return render(request, 'sharespace/search_result_page.html', context=search_context)

    def post(self, request):
        search_context = {}
        return render(request, 'sharespace/search_result_page.html', context=search_context)


class LoanCompleteNotificationView(View):
    @method_decorator(login_required)
    def get(self, request, notification_slug):
        # coded form manually
        # form = None

        notif = Notification.objects.get(notif_slug=notification_slug)
        if not notif.notif_read:
            notif.notif_read = True
            notif.save()
        print(notif)
        sender = notif.notif_origin
        receiver = notif.notif_target
        title = notif.notif_title
        body = notif.notif_body
        context = {
            'notification': notif,
            'from_user': sender,
            'to_user': receiver,
            'title': title,
            'body': body,
            'notification_slug': notification_slug,
            'read': notif.notif_read,
            'complete': notif.notif_complete,
        }
        # NEED TO LOOK INTO THIS BETTER - 3 WAY LOGIC
        if notif.notif_complete or (not notif.notif_action_needed):
            context['msg'] = "thank you for actioning this notification \n " \
                             "if you submitted a report please see your reports page for any updates "
            context['complete'] = True

        else:
            context['msg'] = "please select an action for this notification"
        return render(request, 'sharespace/notification_page.html', context=context)

    @method_decorator(login_required)
    def post(self, request, notification_slug):
        print(request)
        input_value = request.POST['action-desired-selection']
        notification = Notification.objects.get(notif_slug=notification_slug)
        if input_value == 'returned-ok':
            message = """ Thank you for confirming that your item was returned correctly
                            and thank you for sharing something with your neighbours
                            hold on tight while we redirect you"""
            context = {'message': message}
            up_dict = extract_us_up(request)
            if up_dict['up'] is not None:
                context['profile_slug'] = up_dict['up'].user_slug

            notification.complete_notif()
            notification.content_object.mark_as_complete_by_lender()

            return render(request, 'sharespace/waiting_page.html', context)
        else:
            slug = slugify("_".join(("loan", notification.subject.loan_slug)))
            return redirect(reverse('sharespace:submit_report', kwargs={'subject_slug': slug}))


class SubmitReportView(View):
    @method_decorator(login_required)
    def get(self, request, subject_slug):
        report_subject = unpack_slug_for_report(subject_slug)
        up_dict = extract_us_up(request)

        if up_dict['up'] is None:
            return HttpResponse("404 user not found")

        up = up_dict['up']

        bound_form_data = {
            'report_sender': up,
            'report_subject': report_subject,
            'report_date_out': date.today(),
        }
        form = SubmitReportForm(bound_form_data)
        context = {'form': form,
                   'subject_slug': subject_slug}

        return render(request, 'sharespace/report.html', context=context)

    def post(self, request, subject_slug):

        print(request.POST)
        form = SubmitReportForm(request.POST)
        if form.is_valid():
            report = form.save(commit=False)
            subject = unpack_slug_for_report(subject_slug)
            if subject is None:
                return HttpResponse("invalid report subject")
            else:
                report.content_object = subject
                report.save()
                return render(request, 'sharespace/waiting_page.html', context = {'message': "your report was "
                                                                                             "submitted correctly. "
                                                                                             "Admin will review and "
                                                                                             "take  appropriate "
                                                                                             "action. We may need to "
                                                                                             "contact you to get more "
                                                                                             "information, "
                                                                                             "so please keep an eye "
                                                                                             "out for any emails from "
                                                                                             "us! "})
        else:
            print("there are report form errors: ", form.errors)


class SubmitPurchaseProposal(View):
    @method_decorator(login_required)
    def get(self, request):
        form = SubmitPurchaseProposalForm()
        return render(request, 'sharespace/submit_purchase_proposal.html', {'form': form})

    @method_decorator(login_required)
    def post(self, request):
        form = SubmitPurchaseProposalForm(request.POST)
        if form.is_valid():
            proposal = form.save(commit=False)
            up_dict = extract_us_up(request)
            submitter = up_dict['up']
            proposal.proposal_submitter = submitter
            print("in submit purch prop view: ", submitter)
            kwargs = {'submitter': submitter}
            print("still in views ", kwargs)
            proposal.save()

            # return HttpResponse("proposal created")

            return redirect(reverse('sharespace:proposal_page', kwargs={'proposal_slug': proposal.proposal_slug}))

        else:
            print(form.errors, "there are errors in proposal form")


@login_required
def purchase_proposal_list_view(request):
    context = {}
    up_dict = extract_us_up(request)
    if up_dict['up'] is not None:
        hood = up_dict['up'].hood
        purch_prop_list = PurchaseProposal.objects.filter(proposal_hood=hood)
        context['list'] = purch_prop_list
    return render(request, 'sharespace/purchase_proposal_list.html', context=context)


class PurchaseProposalPage(View):
    #need to open this view to non-logged in?
    @method_decorator(login_required)
    def get(self, request, proposal_slug):
        print("for some reason this is getting called")
        proposal = PurchaseProposal.objects.get(proposal_slug=proposal_slug)
        up_dict = extract_us_up(request)
        submitter_flag = up_dict['up'] == proposal.proposal_submitter
        proposal_comments = proposal.comments.all()
        subscriber_flag = proposal.proposal_subscribers.filter(user_slug=up_dict['up'].user_slug).exists()
        if proposal.proposal_subs_count > 0:
            price_per_person = round(float(proposal.proposal_price / proposal.proposal_subs_count))
            print("subs flag value :", subscriber_flag)
            return render(request, 'sharespace/purchase_proposal_page.html', {'proposal': proposal,
                                                                              'subs_flag': subscriber_flag,
                                                                              'subm_flag': submitter_flag,
                                                                              'price_per_person': price_per_person,
                                                                              'comments': proposal_comments})
        return render(request, 'sharespace/purchase_proposal_page.html', {'proposal': proposal,
                                                                          'subs_flag': subscriber_flag,
                                                                          'subm_flag': submitter_flag,
                                                                          'comments': proposal_comments})


def ajax_sub_prop_view(request):
    print("in sub ajax view")
    username = request.GET.get('username')
    print(username)
    proposal_slug = request.GET.get('proposal_slug')
    print("printing proposal slug --- ", proposal_slug)
    try:
        us = CustomUser.objects.get(username=username)
        try:
            up = UserProfile.objects.get(user=us)
            try:
                prop = PurchaseProposal.objects.get(proposal_slug=proposal_slug)
                prop.proposal_subscribers.add(up)
                prop.proposal_subs_count += 1
                prop.save()
                price_per_person = round(float(prop.proposal_price / prop.proposal_subs_count))
                return JsonResponse({'subs_count': prop.proposal_subs_count, 'price_per_person': price_per_person})
            except PurchaseProposal.DoesNotExist:
                return HttpResponse("proposal not found")
        except UserProfile.DoesNotExist:
            return HttpResponse("user profile not found")
    except CustomUser.DoesNotExist:
        return HttpResponse("user not found")




def ajax_post_comment(request):
    if request.method == 'POST':
        prop_slug = request.POST['prop_slug']
        up = extract_us_up(request)['up']
        comment_text = request.POST['comment_text']
        date_logged = datetime.now()
        print(comment_text)
        try:
            proposal = PurchaseProposal.objects.get(proposal_slug = prop_slug)
            comment = CommentToProposal.objects.get_or_create(comment_author = up, comment_text=comment_text,
                                                      comment_date = date_logged, comment_subject = proposal)[0]

            print(comment)
            context= {
                'comment_text': comment_text,
                'comment_author' : up,
                'date' : date_logged,
            }

            return render(request, 'sharespace/comment_body.html', context=context)

        except PurchaseProposal.DoesNotExist:
            print("no purchase proposal found")
            return HttpResponse("no proposal found")
    else:
        return HttpResponse("wrong request type")

def ajax_unsub_prop_view(request):
    print("in UNsub ajax view")
    username = request.GET.get('username')
    print(username)
    proposal_slug = request.GET.get('proposal_slug')
    print("printing proposal slug in un sub--- ", proposal_slug)
    try:
        us = CustomUser.objects.get(username=username)
        try:
            up = UserProfile.objects.get(user=us)
            try:
                prop = PurchaseProposal.objects.get(proposal_slug=proposal_slug)
                qset = prop.proposal_subscribers.filter(user_slug=up.user_slug)

                if qset.exists():
                    print("removing user")
                    prop.proposal_subscribers.remove(up)
                    prop.proposal_subs_count -= 1
                    prop.save()
                    price_per_person = round(float(prop.proposal_price / prop.proposal_subs_count))
                    return JsonResponse({'subs_count': prop.proposal_subs_count, 'price_per_person': price_per_person})
                else:
                    HttpResponse("not a sub")

                return HttpResponse("all done")
            except PurchaseProposal.DoesNotExist:
                return HttpResponse("proposal not found")
        except UserProfile.DoesNotExist:
            return HttpResponse("user profile not found")
    except CustomUser.DoesNotExist:
        return HttpResponse("user not found")


# return HttpResponse("all done")
# ---------------- HELPER FUNCTIONS --------------


def unpack_slug_for_report(slug):
    print("views - 900 - log: printing slug ", slug)

    if slug.find("loan") >= 0:
        loan = Loan.objects.get(loan_slug=slug)

        return loan
    elif slug.find("item") >= 0:
        item = Item.objects.get(item_slug = slug)

        return item
    else:
        print("submitting report for non-linked enetity")
        return None


def get_user_notification(up):
    try:
        notification_list = up.received.all().filter(notif_complete=False)
        print("got notification list, print:")
        for n in notification_list:
            print("something? Anything??!!")
            print("not: ", n)
        return notification_list

    except Notification.DoesNotExist:
        print("no notification to pass")
        return []


def create_address(adr_dict):
    hood = Neighbourhood.objects.get_or_create(nh_post_code=adr_dict.POST['postcode'])[0]
    item_adr = Address.objects.get_or_create(address_line_1=adr_dict.POST['adr_line_1'],
                                             address_line_2=adr_dict.POST['adr_line_2'],
                                             address_line_3=adr_dict.POST['adr_line_3'],
                                             address_line_4=adr_dict.POST['adr_line_4'],
                                             city=adr_dict.POST['city'],
                                             locality=adr_dict.POST['locality'],
                                             county=adr_dict.POST['county'],
                                             adr_hood=hood)[0]

    return item_adr

def process_add_item_form(request):

    owner_usernames_list = []
    for k,v in request.POST.items():
        print(f"view - 60 - log : printin k v pairs in request.post : {k} - {v}")
        if request.POST[k] == k or k == 'owner-selector':
            owner_usernames_list.append(v)

    owners_list = []
    if owner_usernames_list:
        for o in owner_usernames_list:
            try:
                user = CustomUser.objects.get(username=o)
                try:
                    up = UserProfile.objects.get(user=user)
                    owners_list.append(up)
                except UserProfile.DoesNotExist:
                    print("no up")
                    return {'form_valid': False, 'msg': 'no user profile found'}
            except CustomUser.DoesNotExist:
                print("no user")
                return {'form_valid': False, 'msg': 'no user found'}

        print("views - 70 - log: compiled list of owners for this item: ", owners_list)
    item_guardian = None
    if 'guardian-selector-nm' in request.POST:
        try:
            user = CustomUser.objects.get(username=request.POST['guardian-selector-nm'])
            try:
                item_guardian = UserProfile.objects.get(user=user)
                owners_list.append(item_guardian)

            except UserProfile.DoesNotExist:
                print("no up")
                return {'form_valid': False, 'msg': f"no user profile found for item guardian. selected was: {request.POST['guardian-selector-nm']}"}
        except CustomUser.DoesNotExist:
            print("no user")
            return {'form_valid': False, 'msg': f"no user found for item guardian. selected was: {request.POST['guardian-selector-nm']}"}
    else:
        up_dict = extract_us_up(request)
        if up_dict['up'] is None:
            return {'form_valid': False, 'msg': 'no user found'}
        else:
            item_guardian = up_dict['up']
            owners_list.append(up_dict['up'])

    item_name = request.POST['name']
    item_description = request.POST['description']
    main_cat_name = request.POST['main_category']
    main_cat = Category.objects.get(name=main_cat_name)
    sub_cat_name = request.POST['sec_category']
    sec_cat = Sub_Category.objects.get(name=sub_cat_name)
    max_loan_len = int(request.POST['max_loan_len'])
    item_address = create_address(request)

    form_dict = {
        'owners' : owners_list,
        'guardian' : item_guardian,
        'address' : item_address,
        'main_cat':main_cat,
        'sec_cat': sec_cat,
    }

    validation = validate_add_item_form(form_dict)

    if validation['validation']:
        form_dict['form_valid'] = True
        form_dict['name'] = item_name
        form_dict['description'] = item_description
        form_dict['max_loan_len'] = max_loan_len
        pp(form_dict)
        return form_dict
    else:
        return {'form_valid': False, 'msg': validation['msg']}
