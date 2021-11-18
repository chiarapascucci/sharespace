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
    if out_date < now():
        return False
    if timedelta(days=0) <  due_date - out_date  <= max_len and due_date<= (now()+timedelta(days=90)):
        print(f"form validation - 40 - log : out on {out_date}, back on {due_date}, delta (loan duration) {(due_date - out_date)}, max len {max_len}")
        return True
    else:
        return False

def validate_item(item, date_from, date_to):

    if date_from.date() == now().date():
        if not item.available:
            return False
        item_q_set = item.on_loan.filter(Q(status = 'pen') | Q(status = 'act'))
        if item_q_set.exists():
            return False
    else:
        item_q_set = item.on_loan.filter(Q(out_date__lte = date_to, due_date__gte = date_from))
        if item_q_set.exists():
            return False

    return True


def validate_user(up, date_out, date_due):
    status_dict = up.can_book_check
    if status_dict['unactioned_notif']:
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




