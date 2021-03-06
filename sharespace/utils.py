"""

    file to store custom utils function for this application

"""

__author__ = "Chiara Pascucci"

from calendar import HTMLCalendar
from sharespace.models import UserProfile, CustomUser, Item, Loan, Notification, PurchaseProposal


# this class extends HTMLCalendar python class
# it is used to create a string in HTML syntax to display an item's availability in a given month
class BookingCalendar(HTMLCalendar):

    def __init__(self, item=None):
        super(BookingCalendar, self).__init__()
        self.item = item

    def formatday(self, day, weekday, bk_flag=False):
        if day == 0:
            return '<td class="%s">&nbsp;</td>' % self.cssclass_noday
        else:
            if bk_flag:
                return '<td class="%s" style="background-color:#FF0000">%d</td>' % (self.cssclasses[weekday], day)
            else:
                return '<td class="%s">%d</td>' % (self.cssclasses[weekday], day)

    def formatweek(self, theweek, days_unavail_set=()):
        """
        Return a complete week as a table row.
        """
        if not days_unavail_set:
            s = ''.join(self.formatday(d, wd) for (d, wd) in theweek)
            return '<tr>%s</tr>' % s
        else:
            s = ''.join(self.formatday(d, wd, (d in days_unavail_set)) for (d, wd) in theweek)
            return '<tr>%s</tr>' % s

    def formatmonth(self, theyear, themonth, withyear=True):
        """
        Return a formatted month as a table.
        """
        # # # # Here is where the get overall item availability logic is triggered
        # # # getting unavail days as in for easier HTML formatting
        loan_days_set = self.item.get_days_unavailable_in_month_as_ints(themonth, theyear)

        v = []
        a = v.append
        a('<table border="0" cellpadding="0" cellspacing="0" class="%s">' % (
            self.cssclass_month))
        a('\n')
        a(self.formatmonthname(theyear, themonth, withyear=withyear))
        a('\n')
        a(self.formatweekheader())
        a('\n')
        for week in self.monthdays2calendar(theyear, themonth):

            a(self.formatweek(week, days_unavail_set=loan_days_set))
            a('\n')
        a('</table>')
        a('\n')
        return ''.join(v)


# generates calendar for current month + 3 months
def get_booking_calendar_for_item_for_month(item, month:int, year:int):
    cal = BookingCalendar(item=item)
    return cal.formatmonth(year, month)


def extract_us_up (request):
    if request.user.is_anonymous:
        print("anonymous user")
        return {'us': None, 'up': None}
    else:
        try:
            username = request.user.get_username()
            print("in extract user method. this is the result of get_username ", username)
            us = CustomUser.objects.get(email = username)

            try:
                up = UserProfile.objects.get(user = us)
                return {'us': us, 'up' : up}

            except UserProfile.DoesNotExist:
                print("no user profile here (views/200")
                return {'us' : us, 'up' : None}

        except CustomUser.DoesNotExist:
            print("no user here (views)")
            return {'us': None, 'up': None}


# helper functions to views.py
# they are use to check a user's permission with respect to the page they are trying to access

def test_item_ownership(request, item_slug):
    try:
        item = Item.objects.get(item_slug=item_slug)
        up = extract_us_up(request)['up']
        if up is None:
            return False
        else:
            if not item.owner.filter(user_slug=up.user_slug).exists():
                return False
            else:
                return True
    except Item.DoesNotExist:
        return False


def test_loan_ownership(request, loan_slug):
    try:
        loan = Loan.objects.get(loan_slug=loan_slug)
        up = extract_us_up(request)['up']
        if up is None:
            return False
        else:
            if not loan.requestor == up:
                return False
            else:
                return True
    except Loan.DoesNotExist:
        return False


def test_notif_ownership(request, notif_slug):
    up = extract_us_up(request)['up']
    if up is not None:
        try:
            notif = Notification.objects.get(notif_slug=notif_slug)
            if notif.notif_target == up:
                return True
            else:
                return False
        except Notification.DoesNotExist:
            return False
    else:
        return False


def test_proposal_ownership(request, prop_slug):
    up = extract_us_up(request)['up']
    if up is None:
        return False
    else:
        try:
            proposal = PurchaseProposal.objects.get(proposal_contact=prop_slug)
            if proposal.proposal_submitter == up:
                return True
            else:
                return False
        except PurchaseProposal.DoesNotExist:
            return False

