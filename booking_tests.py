import os
from datetime import timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sharespace_project.settings')

import django
django.setup()
from django.contrib.auth.hashers import PBKDF2PasswordHasher, make_password
from sharespace.models import Item, UserProfile, Category, SubCategory, Neighbourhood, Loan, ReportToAdmin, Notification, ItemBooking, range_overlap_check_true_false, bookings_overlap_check_and_count
import random
from django.utils.timezone import now
from django.contrib.auth.models import User
from django.core.files import File
import sharespace_project.settings as Psettings
from sharespace.utils import BookingCalendar, get_booking_calendar_for_item_for_month

def booking_test():
    all_items = Item.objects.all()

    all_ups = UserProfile.objects.all()

    items_list = list(all_items)

    up_list = list(all_ups)

    today = now().today()

    tomorrow = today + timedelta(days=1)

    one_week = today + timedelta(days=7)

    eight_days = today + timedelta(days=8)

    nine_days = today + timedelta(days=9)

    ten_days = today + timedelta(days=10)

    two_weeks = today + timedelta(days=14)

    th_days = today + timedelta(days=13)

    egth_days = today + timedelta(days=18)

    three_weeks = today + timedelta(days=21)

    bok_0 = ItemBooking.objects.get_or_create(booking_requestor=up_list[0], booking_item=items_list[0], booking_from=one_week,
                                      booking_to=two_weeks)[0]

    bok_1 = ItemBooking.objects.get_or_create(booking_requestor=up_list[1], booking_item=items_list[0], booking_from=nine_days,
                                      booking_to=three_weeks)[0]

    bok_2 = ItemBooking.objects.get_or_create(booking_requestor=up_list[2], booking_item=items_list[1], booking_from=tomorrow,
                                      booking_to=two_weeks)[0]

    bok_3 = ItemBooking.objects.get_or_create(booking_requestor=up_list[1], booking_item=items_list[1], booking_from=nine_days,
                                      booking_to=two_weeks)[0]

    bok_4 = ItemBooking.objects.get_or_create(booking_requestor=up_list[0], booking_item=items_list[0], booking_from=tomorrow,
                                      booking_to=two_weeks)[0]

    bok_5 = ItemBooking.objects.get_or_create(booking_requestor=up_list[1], booking_item=items_list[0], booking_from=eight_days,
                                      booking_to=egth_days)[0]

    bok_6 = ItemBooking.objects.get_or_create(booking_requestor=up_list[1], booking_item=items_list[0], booking_from=ten_days,
                                      booking_to=th_days)[0]

    booking_list = [bok_0, bok_1, bok_2, bok_3, bok_4, bok_5, bok_6]
    date_format = "%d/%m"
    booking_list.sort(key= lambda x: x.booking_from, reverse=False)
    for i in booking_list:
        print("booking: {} booked {}, from {} until {}".format(i.booking_requestor, i.booking_item, i.booking_from.strftime(date_format), i.booking_to.strftime(date_format)))


    print(" max overlap method test. Expected 5, output {}".format(bookings_overlap_check_and_count(booking_list)))

    print("overlap check method test. Expected True, output {}".format(range_overlap_check_true_false(booking_list)))

    print(up_list[1].max_no_of_items)

    print(up_list[1].can_book_check(nine_days, two_weeks))

    print("----------------------------------------")

    print(get_booking_calendar_for_item_for_month(items_list[0], 11))

if __name__ == '__main__':

    print('running test script')
    booking_test()