


def get_list_of_days(self):
    day_list = []
    day_list.append(self.booking_from)
    delta = int((self.booking_to - self.booking_from).days)
    for i in range(1, delta + 1):
        day = self.booking_from + timedelta(days=i)
        # print(day)
        day_list.append(day)

    return day_list


def clean(self):
    # checking that entered dates make sense
    # and that the requested len of the booking does not exceed the max len of loan for this item
    today = django.utils.timezone.now().date()
    max_len_of_booking = timedelta(days=self.booking_item.max_loan_len * 7)

    min_start = today + timedelta(days=1)
    max_start = today + timedelta(days=AVAILABILITY_RANGE - 2)

    if not min_start > self.booking_from > max_start:
        raise ValidationError

    if not timedelta(days=3) > self.booking_to - self.booking_from > max_len_of_booking:
        raise ValidationError

    # check item availability
    # helper function takes the requested booking date and checks that there are no bookings during those dates on the item
    item_is_available = self.booking_item.check_availability_from_to(self.booking_from, self.booking_to)
    if not item_is_available:
        raise ValidationError

    # check if user can borrow
    # i.e. during the requested period the user cannot exceed their max num of items
    user_can_book = self.booking_requestor.can_book_check(self.booking_from, self.booking_to)

    if not user_can_book:
        raise ValidationError


    # get list of bookings, convert that in a list of date ranges
    # check if overlap
    # if overlap return true, else false
def range_overlap_check_true_false(booking_list):
    """
    :param booking_list: parameter that it takes
    :return: what it returns
    """
    MyDateRange = namedtuple('MyDateRange', ['start_date', 'end_date'])
    ranges_list = []

    for b in booking_list:
        r = MyDateRange(start_date=b.booking_from, end_date=b.booking_to)
        ranges_list.append(r)

    sorted_list = sorted(ranges_list, key=attrgetter('start_date'))

    print("printing sorted list: ", sorted_list)

    for i in range(0, len(sorted_list)-1):
        if overlap(sorted_list[i], sorted_list[i+1]):
            return True

    return False


# this method takes a list of bookings
# returns the max number of overlaps between bookings in the list
# list is sorted
def bookings_overlap_check_and_count(booking_list):

    if not booking_list or len(booking_list)==1:
        return 0

    booking_list.sort(key=lambda x: x.booking_from, reverse=False)
    print("in models, booking overlap check and count, printin sorted list: ", booking_list)

    num_list = []
    for i in range(0, len(booking_list)-2):
        overlap_count = 0
        for k in range(1, len(booking_list)-1):
            if booking_list[i].booking_to >= booking_list[k].booking_from:
                overlap_count += 1
        num_list.append(overlap_count)

    return max(num_list)