from calendar import HTMLCalendar
from datetime import datetime
from django.utils.timezone import now

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

    def formatweek(self, theweek, bk_set=()):
        """
        Return a complete week as a table row.
        """
        if not bk_set:
            s = ''.join(self.formatday(d, wd) for (d, wd) in theweek)
            return '<tr>%s</tr>' % s
        else:
            s = ''.join(self.formatday(d, wd, (d in bk_set)) for (d, wd) in theweek)
            return '<tr>%s</tr>' % s




    def formatmonth(self, theyear, themonth, withyear=True):
        """
        Return a formatted month as a table.
        """
        bk_set = self.item.get_days_booked_in_month(themonth)

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

            a(self.formatweek(week, bk_set=bk_set))
            a('\n')
        a('</table>')
        a('\n')
        return ''.join(v)


# need method that generate the right item - booking set pairing given an item
# generates calendar for current month + 3 months
def get_booking_calendar_for_item_for_month(item, month:int):
    cal = BookingCalendar(item=item)
    return cal.formatmonth(now().year, month)
