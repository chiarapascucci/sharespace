import os
from datetime import timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sharespace_project.settings')

import django
django.setup()
from django.contrib.auth.hashers import PBKDF2PasswordHasher, make_password
from sharespace.models import Item, UserProfile, Category, Sub_Category, Neighbourhood, Loan, UserToAdminReportNotAboutUser, Notification, ItemBooking, range_overlap_check
import random
from django.utils.timezone import now
from django.contrib.auth.models import User
from django.core.files import File
import sharespace_project.settings as Psettings

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


    booking_list = []
    booking = ItemBooking.objects.get_or_create(booking_requestor=up_list[0], booking_item=items_list[0], booking_from=one_week,
                                      booking_to=two_weeks)[0]

    booking_one = ItemBooking.objects.get_or_create(booking_requestor=up_list[1], booking_item=items_list[0], booking_from=nine_days,
                                      booking_to=two_weeks)[0]

    booking_list.append(booking_one)
    booking_list.append(booking)


    print(booking_list)

    print(range_overlap_check(booking_list))

if __name__ == '__main__':

    print('running test script')
    booking_test()