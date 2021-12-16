from collections import namedtuple
from datetime import timedelta, datetime, date
from operator import attrgetter

from django.core.exceptions import ValidationError
from django.db.models import Q
from django.utils.timezone import now
import pytz
from sharespace.models import Item
from sharespace.utils import extract_us_up

BOOKING_RANGE = 90

utc = pytz.UTC


def validate_borrowing_form(item, up, out_date, due_date):
    date_out = datetime.strptime(out_date, "%Y-%m-%d").replace(tzinfo=utc)
    date_due = datetime.strptime(due_date, "%Y-%m-%d").replace(tzinfo=utc)

    max_loan_len = timedelta(days=(item.max_loan_len * 7))

    outcome = {'form_valid': False}

    if not validate_user(up, date_out, date_due):
        outcome['msg'] = "you cannot borrow any item at moment. Please ensure that you do not have unactioned notifications or overdue loans"
        return outcome

    # validate dates
    if not validate_dates_loan(date_out, date_due, max_loan_len):
        # raise error
        outcome['msg'] = "the dates entered are not valid"
        return outcome

    if not item.location.adr_hood == up.hood :
        outcome['msg'] = "you do not have access to this item"
        return outcome

    if not validate_item(item, date_out, date_due):
        outcome['msg'] = 'this item is not available for the selected dates'
        return outcome

    outcome['form_valid'] = True
    outcome['msg']= "loan created"
    print("form validation successful")
    return outcome


def validate_dates_loan(out_date, due_date, max_len):
    if out_date.day < now().day:
        return False
    if timedelta(days=0) <  due_date - out_date  <= max_len and due_date<= (now()+timedelta(days=90)):
        print(f"form validation - 40 - log : out on {out_date}, back on {due_date}, delta (loan duration) {(due_date - out_date)}, max len {max_len}")
        return True
    else:
        return False


def validate_item(item, date_from, date_to):

    if date_from.date() == now().date():
        if not item.available:
            print("form validation - 60 - log: item not available from today")
            return False
        item_q_set = item.on_loan.filter(Q(status = 'pen') | Q(status = 'act'))
        if item_q_set.exists():
            print("form validation - 60 - log: there are pending or active loans on this item")
            return False
    else:
        item_q_set = item.on_loan.filter(Q(out_date__lte = date_to, due_date__gte = date_from, status__in=['act', 'fut', 'pen']))
        if item_q_set.exists():
            print("form validation - 70 - log: other loans overlap with this request")
            return False

    return True


def validate_user(up, date_out, date_due):
    status_dict = up.can_borrow_check()
    if status_dict['unactioned_notif']:
        return False
    elif status_dict['overdue_loan']:
        return False

    if date_out.date() == now().date():
        if status_dict['max_no_of_items'] or not up.can_borrow:
            return False

    loan_q_set = up.loans.filter(Q(out_date__lte=date_due, due_date__gte=date_out, status__in=['fut', 'act']))
    if loan_q_set.exists():
        loans_list = list(loan_q_set)
        overlaps = count_loans_overlap(loans_list)
        if overlaps > up.max_no_of_items:
            return False

    return True


def count_loans_overlap(loan_list):
    if not loan_list or len(loan_list)==1:
        return 0

    loan_list.sort(key=lambda x : x.out_date, reversed=False)
    print("in form val, booking overlap check and count, printin sorted list: ", loan_list)

    num_list=[0]

    for i in range(0, len(loan_list)-2):
        overlap_count = 0
        for k in range(1, len(loan_list)-1):
            if loan_list[i].due_date >= loan_list[k].booking_from:
                overlap_count +=1
            num_list.append(overlap_count)

    return max(loan_list)


def validate_add_item_form(dict):
    cat_val = validate_categories(cat=dict['main_cat'], sub_cat=dict['sec_cat'])
    if not cat_val:
        return {'validation': False, 'msg': 'cat and sub cat combination is not valid'}

    if dict['guardian'] not in dict['owners']:
        return {'validation': False, 'msg': 'selected guardian is not an owner'}

    if not validate_location(up_list=dict['owners'], address=dict['address']):
        return {'validation': False, 'msg': 'one or more of the owners are not part of the right hood'}

    print(dict['phone'], len(dict['phone']))
    if not validate_phone(dict['phone']):
        return {'validation': False, 'msg': 'Please enter a valid phone number'}

    return {'validation': True, 'msg': 'all good'}


def validate_categories(cat, sub_cat):
    if sub_cat.parent == cat:
        return True
    else:
        return False


def validate_location(up_list, address=None):
    if address is None:
        for i in range(0, len(up_list)-2):
            if not (up_list[i].hood == up_list[i+1].hood):
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
