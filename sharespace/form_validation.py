"""
    custom file that provides helper functions to validate different forms in the app which take user input
"""

__author__ = "Chiara Pascucci"

from datetime import timedelta, datetime, date
from django.db.models import Q
from django.utils.timezone import now
import pytz

# max days an item can be booked for
BOOKING_RANGE = 90
# set global timezone as app meant to be used in the UK only
utc = pytz.UTC


# this function is called to check that data submitted with a loan request is valid and meets the application's rules
def validate_borrowing_form(item, up, out_date, due_date):
    date_out = datetime.strptime(out_date, "%Y-%m-%d").replace(tzinfo=utc)
    date_due = datetime.strptime(due_date, "%Y-%m-%d").replace(tzinfo=utc)

    max_loan_len = timedelta(days=(item.max_loan_len * 7))

    outcome = {'form_valid': False}

    # calling different helper functions to validate different aspects of the form
    # if any of these checks fails a negative outcome is returned right away (false)
    if not validate_user(up, date_out, date_due):
        outcome['msg'] = "you cannot borrow any item at moment. Please ensure that you do not have unactioned " \
                         "notifications or overdue loans "
        return outcome

    # validate dates
    if not validate_dates_loan(date_out, date_due, max_loan_len):
        outcome['msg'] = "the dates entered are not valid"
        return outcome

    # check that the user is located in the same neighbourhood as the item
    if not item.location.adr_hood == up.hood:
        outcome['msg'] = "you do not have access to this item"
        return outcome

    # check that the item is infact available for the selected dates
    if not validate_item(item, date_out, date_due):
        outcome['msg'] = 'this item is not available for the selected dates'
        return outcome

    # summarises outcome in dictionary before returning
    outcome['form_valid'] = True
    outcome['msg'] = "loan created"

    return outcome


def validate_dates_loan(out_date, due_date, max_len):
    # checkout date is in the past
    if out_date.date() < now().date():
        print(f"form validation - 40 - log : DATES VALIDATION NOT PASSED: out on {out_date}, back on {due_date}, "
              f"delta (loan duration) {(due_date - out_date)}, max len {max_len}")
        return False
    # loan timeline is too short or too long
    if timedelta(days=0) < due_date - out_date <= max_len and due_date <= (now() + timedelta(days=90)):
        print(f"form validation - 40 - log : out on {out_date}, back on {due_date}, delta ("
              f"loan duration) {(due_date - out_date)}, max len {max_len}")
        return True
    else:
        print(
            f"form validation - 40 - log : DATES VALIDATION NOT PASSED: out on {out_date}, back on {due_date}, delta "
            f"(loan duration) {(due_date - out_date)}, max len {max_len}")
        return False


def validate_item(item, date_from, date_to):
    # if loan is from current date
    if date_from.date() == now().date():
        # check if item is avaible
        if not item.available:
            print("form validation - 60 - log: item not available from today")
            return False

        # check if there are any pending or active loans on the item
        item_q_set = item.on_loan.filter(Q(status='pen') | Q(status='act'))
        if item_q_set.exists():
            print("form validation - 60 - log: there are pending or active loans on this item")
            return False
    else:
        # check if any loan with status other than complete overlaps with the requested dates
        item_q_set = item.on_loan.filter(
            Q(out_date__lte=date_to, due_date__gte=date_from, status__in=['act', 'fut', 'pen']))
        if item_q_set.exists():
            print("form validation - 70 - log: other loans overlap with this request")
            return False

    return True


def validate_user(up, date_out, date_due):
    # checks if the user is currently allowed to borrow
    status_dict = up.can_borrow_check()
    if status_dict['unactioned_notif']:
        return False
    elif status_dict['overdue_loan']:
        return False

    if date_out.date() == now().date():
        if status_dict['max_no_of_items'] or not up.can_borrow:
            return False

    # checks if allowing the current request would take the user over their max no of item allowance
    # during the time of the loan
    loan_q_set = up.loans.filter(Q(out_date__lte=date_due, due_date__gte=date_out, status__in=['fut', 'act']))
    if loan_q_set.exists():
        loans_list = list(loan_q_set)
        overlaps = count_loans_overlap(loans_list)
        if overlaps > up.max_no_of_items:
            return False

    return True


# helper function to the check above
def count_loans_overlap(loan_list):
    if not loan_list or len(loan_list) == 1:
        return 0
    loan_list.sort(key=lambda x: x.out_date)
    num_list = [0]

    for i in range(0, len(loan_list) - 2):
        overlap_count = 0
        for k in range(1, len(loan_list) - 1):
            if loan_list[i].due_date >= loan_list[k].out_date:
                overlap_count += 1
            num_list.append(overlap_count)

    return max(num_list)


# function used to validate data input by user when adding item to the website
def validate_add_item_form(item_dict):
    cat_val = validate_categories(cat=item_dict['main_cat'], sub_cat=item_dict['sec_cat'])
    if not cat_val:
        return {'validation': False, 'msg': 'cat and sub cat combination is not valid'}

    if item_dict['guardian'] not in item_dict['owners']:
        return {'validation': False, 'msg': 'selected guardian is not an owner'}

    if not validate_location(up_list=item_dict['owners'], address=item_dict['address']):
        return {'validation': False, 'msg': 'one or more of the owners are not part of the right hood'}

    if not validate_phone(item_dict['phone']):
        return {'validation': False, 'msg': 'Please enter a valid phone number'}

    return {'validation': True, 'msg': 'all good'}


# checks that category and sub category pairing is valid
def validate_categories(cat, sub_cat):
    if sub_cat.parent == cat:
        return True
    else:
        return False


# check that all selected owners are in the same neighbourhood as the item
def validate_location(up_list, address=None):
    if address is None:
        for i in range(0, len(up_list) - 2):
            if not (up_list[i].hood == up_list[i + 1].hood):
                return False

    else:
        hood = address.adr_hood
        for up in up_list:
            if not (up.hood == hood):
                return False

    return True


def validate_phone(phone):
    print(len(phone))
    if len(phone) < 7:
        print("phone number too short")
        return False
    if not phone[0] == '+':
        print("not including +")
        return False
    if phone == '+00000000' or phone == '+12345678':
        print("bad number")
        return False
    return True
