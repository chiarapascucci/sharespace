import uuid
from operator import attrgetter
from calendar import monthrange
from pprint import pprint

import django.utils.timezone
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q

from django.db.models.fields import CharField
from django.db.models.fields.related import ForeignKey, OneToOneField
from django.template.defaultfilters import slugify
from django.contrib.auth.models import AbstractUser
from datetime import datetime, date, time, timedelta
from django.core.validators import MaxValueValidator
from django.utils.timezone import now as default_time
from collections import namedtuple
from phonenumber_field.modelfields import PhoneNumberField


from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType

from sharespace.managers import MyUserManager

from sharespace.model_fields import EmailFieldLowerCase


MAX_LENGTH_TITLES = 55
MAX_LENGTH_TEXT = 500
AVAILABILITY_RANGE = 90


class Neighbourhood(models.Model):
    # name = models.CharField(max_length=MAX_LENGTH_TITLES, blank = False)
    nh_post_code = models.CharField(primary_key=True,
                                    max_length=8)  # need to devise something to enforce valid postcodes
    description = models.CharField(max_length=MAX_LENGTH_TEXT, blank=True)
    nh_slug = models.SlugField()

    def save(self, *args, **kwargs):
        self.nh_slug = slugify(self.nh_post_code)
        super(Neighbourhood, self).save(*args, **kwargs)

    def __str__(self):
        return self.nh_post_code


class Address(models.Model):
    address_line_1 = models.CharField(max_length=MAX_LENGTH_TITLES, blank=False)
    address_line_2 = models.CharField(max_length=MAX_LENGTH_TITLES, default='')
    address_line_3 = models.CharField(max_length=MAX_LENGTH_TITLES, default='')
    address_line_4 = models.CharField(max_length=MAX_LENGTH_TITLES, default='')
    locality = models.CharField(max_length=MAX_LENGTH_TITLES, default='')
    city = models.CharField(max_length=MAX_LENGTH_TITLES, default='')
    county = models.CharField(max_length=MAX_LENGTH_TITLES, default='')
    country = models.CharField(max_length=MAX_LENGTH_TITLES, default='United Kingdom')

    adr_hood = models.ForeignKey(Neighbourhood, blank=False, on_delete=models.CASCADE)

    def __str__(self):
        address_str = str(self.address_line_1) + "\n" + str(self.address_line_2) + "\n" + str(
            self.city) + "\n" + self.adr_hood.nh_post_code
        return address_str


# class Reportable(models.Model):
#   pass


class Category(models.Model):
    name = models.CharField(primary_key=True, max_length=MAX_LENGTH_TITLES)
    description = models.TextField(max_length=MAX_LENGTH_TEXT, blank=True)
    point_value = models.IntegerField(default=1)
    cat_slug = models.SlugField(unique=True)
    cat_img = models.URLField(blank=True)


    def save(self, *args, **kwargs):
        self.cat_slug = slugify(self.name)
        super(Category, self).save(*args, **kwargs)

    class Meta:
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name


class Sub_Category(models.Model):
    name = models.CharField(primary_key=True, max_length=MAX_LENGTH_TITLES)
    description = models.TextField(max_length=MAX_LENGTH_TEXT)
    point_value = models.IntegerField(default=1)
    parent = models.ForeignKey(Category, on_delete=models.CASCADE)
    sub_cat_slug = models.SlugField(unique=True)

    def save(self, *args, **kwargs):
        self.sub_cat_slug = slugify(self.name)
        super(Sub_Category, self).save(*args, **kwargs)

    class Meta:
        verbose_name_plural = 'Secondary Categories'

    def __str__(self):
        return self.name



def get_list_of_days_as_dates(date_from, date_to):
    day_list = []
    day_list.append(date_from)
    delta = int((date_to - date_from).days)
    for i in range(1, delta + 1):
        day = date_from + timedelta(days=i)
        day_list.append(day)
    return day_list

def get_list_of_days_as_ints(date_from, date_to):
    day_list = get_list_of_days_as_dates(date_from, date_to)
    day_int_list = []
    for d in day_list:
        day_int_list.append(d.days)

class CustomUser(AbstractUser):
    username = models.CharField(max_length=MAX_LENGTH_TITLES, unique=True)
    email = EmailFieldLowerCase('email address', unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', ]

    objects = MyUserManager()

    def __str__(self):
        return self.email


class UserProfile(models.Model):
    user = OneToOneField(CustomUser, on_delete=models.CASCADE)
    bio = models.CharField(max_length=MAX_LENGTH_TEXT, blank=True)
    picture = models.ImageField(upload_to='profile_images', blank=True,
                                default='profile_images/default_profile_image.png')
    user_slug = models.SlugField(unique=True)
    user_post_code = CharField(max_length=8)
    has_unactioned_notif = models.BooleanField(default=False)
    max_no_of_items = models.PositiveIntegerField(default=1)
    curr_no_of_items = models.PositiveIntegerField(default=0)
    can_borrow = models.BooleanField(default=True)
    hood = models.ForeignKey(Neighbourhood,
                             on_delete=models.CASCADE)  # will need to manage or prevent situation where a neighbourhood is deleted
    contact_details = PhoneNumberField(blank=True, null = True)

    def set_hood(self, user_post_code):
        f_user_post_code = user_post_code.strip().replace(' ', '').lower()
        self.hood = Neighbourhood.objects.get_or_create(nh_post_code=f_user_post_code)[0]
        return self

    def can_borrow_check(self):
        flags = {}
        if self.curr_no_of_items >= self.max_no_of_items:
            flags['max_no_of_items'] = True
        else:
            flags['max_no_of_items'] = False

        notif_list = self.received.filter(notif_action_needed=True, notif_complete=False)
        if notif_list.exists():
            flags['unactioned_notif'] = True
        else:
            flags['unactioned_notif'] = False

        return flags


    def save(self, *args, **kwargs):
        self.user_slug = slugify(self.user.username)
        self.user_post_code = self.user_post_code.strip().replace(' ', '').lower()
        print("in profile save method curr no of items", self.curr_no_of_items)
        flags = self.can_borrow_check()
        self.can_borrow = not (flags['unactioned_notif'] or flags['max_no_of_items'])
        self.has_unactioned_notif = flags['unactioned_notif']
        super(UserProfile, self).save(*args, **kwargs)


    def __str__(self):
        return self.user.username


class Notification(models.Model):
    notif_time_stamp = models.DateTimeField(default=default_time)
    notif_read = models.BooleanField(default=False)
    notif_action_needed = models.BooleanField(default=False)
    notif_complete = models.BooleanField(default=False)
    notif_slug = models.SlugField(unique=True, default=uuid.uuid4)
    notif_origin = models.ForeignKey(CustomUser, null=False, on_delete=models.CASCADE, related_name='sent')
    notif_target = models.ForeignKey(UserProfile, null=False, on_delete=models.CASCADE, related_name='received')
    notif_title = models.CharField(max_length=MAX_LENGTH_TITLES, default="you have a notification")
    notif_body = models.TextField(max_length=MAX_LENGTH_TEXT,
                                  default="please ensure you action this notification if necessary")

    # content type relation
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.CharField(max_length=200)
    content_object = GenericForeignKey()
    def complete_notif(self):
        self.notif_complete=True
        self.notif_action_needed=False
        self.notif_read=True
        self.save()
        self.notif_target.save()

    class Meta:
        ordering = ['notif_time_stamp']

    def __str__(self):
        return "notification: {} - {}".format(self.notif_title, self.content_object)


# helpef function (factory)




class UserToAdminReportNotAboutUser(models.Model):
    report_date_out = models.DateField(default=default_time)
    # report_subject = models.ForeignKey(Reportable, null=False, on_delete=models.CASCADE, related_name='target')
    report_sender = models.ForeignKey(UserProfile, null=False, on_delete=models.CASCADE, related_name='submitter')
    report_title = models.CharField(max_length=MAX_LENGTH_TITLES, blank=False)
    report_body = models.TextField(max_length=MAX_LENGTH_TEXT, blank=False)

    # content type relation
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.CharField(max_length=75)
    content_object = GenericForeignKey()

    def __str__(self):
        return "report - submitted by: {}   target: {}".format(self.report_sender, self.content_type)


class HoodGroup(models.Model):
    group_name = models.CharField(blank=False, null=False, max_length=MAX_LENGTH_TITLES, primary_key=True)
    group_description = models.TextField(blank=True, max_length=MAX_LENGTH_TEXT)
    group_founder = models.ForeignKey(UserProfile, null=False, on_delete=models.CASCADE, related_name='founded')
    group_members = models.ManyToManyField(UserProfile, blank=True, related_name='member_of')
    group_hood = models.ForeignKey(Neighbourhood, blank=False, null=False, on_delete=models.CASCADE)
    group_slug = models.SlugField(null=False)
    group_reported = GenericRelation(UserToAdminReportNotAboutUser)

    def save(self, *args, **kwargs):
        self.group_slug = slugify(self.group_name)
        super(HoodGroup, self).save(*args, **kwargs)


class Item(models.Model):
    max_len_of_loan_choices = [
        (1, '1 week'),
        (2, '2 weeks'),
        (3, '3 weeks'),
        (4, '4 weeks'),
    ]
    item_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=MAX_LENGTH_TITLES)
    description = models.CharField(max_length=MAX_LENGTH_TEXT, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=10.00)
    main_category = models.ForeignKey(Category, on_delete=models.CASCADE)
    sec_category = models.ForeignKey(Sub_Category, on_delete=models.SET_NULL, null=True)
    available = models.BooleanField(default=True)
    owner = models.ManyToManyField(UserProfile, related_name="owned", blank=False)
    guardian = models.ForeignKey(UserProfile, related_name="manages", null=False, on_delete=models.CASCADE)
    # borrowed_by = models.ForeignKey(UserProfile, related_name = "borrowed", blank = True,  on_delete=models.SET_NULL, null = True)
    item_slug = models.SlugField(unique=True)
    location = models.ForeignKey(Address, on_delete=models.CASCADE, blank=False)
    max_loan_len = models.PositiveIntegerField(choices=max_len_of_loan_choices, default=4,
                                               validators=[MaxValueValidator(4)])
    item_post_code = CharField(max_length=8)
    item_reported_to_admin = GenericRelation(UserToAdminReportNotAboutUser)

    def save(self, *args, **kwargs):
        # self.id = uuid.uuid4()
        self.item_slug = slugify("item--{self.item_id}".format(self=self))
        # print(self.owner)
        self.item_post_code = self.location.adr_hood.nh_post_code
        for o in self.owner.all():
            o.max_no_of_items +=1
            o.save()
        print("models - 280 - log: number of owners this item has : ", len(self.owner.all()))
        if len(self.owner.all()) == 1:
            self.guardian = self.owner.first()
        super(Item, self).save(*args, **kwargs)

    def __str__(self):
        return self.name



    # checking that the item is currently available
    # if not checking status of the loan
    # if loan is active due date is returned (item can be booked from then)
    # if loan is pending booking is not permitted (false and None date are returned)
    def check_curr_on_loan_status(self):
        if self.available:
            return {'available' : True, 'due_date': None}
        else:
            loan_q_set = self.on_loan.filter(Q(item_on_loan__item_id=self.item_id), status ='act')
            print(len(loan_q_set), "len of loan q set (checking when item is due back")
            if loan_q_set.exist():
                loan = loan_q_set.first()
                return {'available' : False, 'due_date': loan.due_date}
            else:
                loan_q_set = self.on_loan.filter(Q(item_on_loan__item_id=self.item_id), status='pen')
                if loan_q_set.exists():
                    return {'available': False, 'due_date': None}

    # returns a list of bookings on this item for a given month
    def get_loans_for_month(self, month:int, year:int):
        first_day = datetime.strptime("1-{}-{}".format(month, year), "%d-%m-%Y")
        delta = monthrange(year, month)[1]-1
        last_day = first_day + timedelta(days=delta)
        print("models - 300 - log: month {}, year {}, first day {}, last day {}".format(month, year, first_day, last_day))
        loan_q_set = self.on_loan.filter(out_date__lte=last_day, due_date__gte=first_day, status__in=['act', 'fut', 'pen'])
        loans_list = list(loan_q_set)
        print("models - 300 - log : printing list of loans retrieved for {} on month {}".format(self, month))
        pprint(loans_list)
        return loans_list

    def get_days_unavailable_in_month_as_days(self, month:int, year:int):
        loan_list = self.get_loans_for_month(month, year)
        set_days = set()
        if loan_list:
            for l in loan_list:
                days_list = l.get_list_of_days()
                for d in days_list:
                    if d.month == month:
                        set_days.add(d)
                    else:
                        pass
        print("models - 300 - log: set of days item unavail: ", set_days)
        return set_days

    # returns list of ints representing the days when the item is not available
    # because of active/pending loan or booking in a given month
    def get_days_unavailable_in_month_as_ints(self, month:int, year:int):
        day_set = self.get_days_unavailable_in_month_as_days(month, year)
        days_int_set = set()
        if day_set:
            for day in day_set:
                days_int_set.add(day.date().day)
        print("models - 300 - log : ", days_int_set)
        print("models - 300 - log : ", day_set)
        return days_int_set


class Loan(models.Model):
    ACTIVE = 'act'
    PENDING = 'pen'
    COMPLETED = 'com'
    FUTURE = 'fut'
    STATUS_CHOICES = [
        (ACTIVE, 'Active'),
        (PENDING, 'Pending'),
        (COMPLETED, 'Completed'),
        (FUTURE, 'Future')
    ]
    loan_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    requestor = models.ForeignKey(UserProfile, blank=False, related_name="loans", on_delete=models.CASCADE)
    item_on_loan = models.ForeignKey(Item, blank=False, on_delete=models.CASCADE, related_name="on_loan")
    item_loan_pick_up = models.BooleanField(default=False)
    overdue = models.BooleanField(default=False)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, null = True)
    # active = models.BooleanField(default = True)
    out_date = models.DateTimeField(null=False)
    due_date = models.DateTimeField(null=False)
    len_of_loan = models.PositiveIntegerField(default=1)
    loan_slug = models.SlugField(unique=True)
    loan_reported = GenericRelation(UserToAdminReportNotAboutUser)
    applied_effects_flag = models.BooleanField(default=False)

    loan_notification = GenericRelation(Notification)

    def __str__(self):
        my_str = "{} borrowing {} for {} days".format(self.requestor, self.item_on_loan, self.len_of_loan)
        return my_str

    def save(self, *args, **kwargs):
        self.loan_slug = slugify("loan--{self.loan_id}".format(self=self))
        self.len_of_loan = (self.due_date-self.out_date).days
        print("\n in save method in loan model \n out time: {} \n due time: {} ".format(self.out_date, self.due_date))
        super(Loan, self).save(*args, **kwargs)

    def update_loan(self):
        print("in update loan")
        print(self.status)
        if self.status is None:
            print("loan status is none")
            if self.out_date > default_time():

                self.status = self.FUTURE
                self.save()
                return 1
            else:
                self.status = self.PENDING
                self.apply_loan_effects()
                self.save()
                return 1
        else:
            if self.status == self.COMPLETED:
                return 0
            elif self.status == self.ACTIVE:
                if default_time() > self.due_date:
                    self.overdue = True
                    self.save()
                    return 1
                else:
                    return 0
            elif self.status == self.FUTURE:
                if default_time() > self.out_date:
                    self.status = self.PENDING
                    self.apply_loan_effects()
                    self.save()
                    return 1

    def apply_loan_effects(self):
        self.item_on_loan.available = False
        self.item_on_loan.save()
        self.requestor.curr_no_of_items += 1
        self.requestor.save()

    def confirm_item_picked_up(self):
        self.item_loan_pick_up = True
        self.status = self.ACTIVE
        self.save()

    def mark_as_complete_by_borrower(self):
        """
            act --> pen
        """
        self.status = self.PENDING
        self.save()

# need to consider where to have the item available and change to curr no of item for lender

    def mark_as_complete_by_lender(self):
        """
            pen --> com
        """
        self.status = self.COMPLETED
        self.item_on_loan.available = True
        self.item_on_loan.save()
        self.requestor.curr_no_of_items = self.requestor.curr_no_of_items - 1
        self.requestor.save()
        self.save()

    def get_list_of_days(self):
        day_list = [self.out_date]
        delta = int((self.due_date - self.out_date).days)
        print("models - 400 - log: delta = {}".format(delta))
        for i in range(1, delta+1):
            day = self.out_date + timedelta(days=i)
            print("models 400 -log: day = {}".format(day))
            day_list.append(day)
        return day_list

    def get_full_status(self):
        self.update_loan()
        full_status = {
            'status' : self.status,
            'picked_up': self.item_loan_pick_up,
            'overdue' : self.overdue
        }
        return full_status


def upload_gallery_image(instance, filename):
    return f"images/{instance.item.name}/gallery/{filename}"


class Image(models.Model):
    image = models.ImageField(upload_to=upload_gallery_image)
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name="images")


class PurchaseProposal(models.Model):
    proposal_submitter = models.ForeignKey(UserProfile, blank=False, on_delete=models.CASCADE, related_name="proposals")
    proposal_contact = models.CharField(max_length=MAX_LENGTH_TITLES, blank=False)
    proposal_subscribers = models.ManyToManyField(UserProfile, blank=True, default=None, related_name="interested")
    proposal_item_name = models.CharField(blank=False, max_length=MAX_LENGTH_TITLES)
    proposal_cat = models.ForeignKey(Category, null=False, on_delete=models.CASCADE)
    proposal_sub_cat = models.ForeignKey(Sub_Category, null=True, on_delete=models.SET_NULL)
    proposal_item_description = models.TextField(blank=False, max_length=MAX_LENGTH_TEXT)
    proposal_price = models.DecimalField(max_digits=10, decimal_places=2, blank=False)
    proposal_hood = models.ForeignKey(Neighbourhood, null=False, on_delete=models.CASCADE)
    proposal_slug = models.SlugField(primary_key=True)
    proposal_active = models.BooleanField(default=True)
    proposal_purchased = models.BooleanField(default=False)
    proposal_timestamp = models.DateTimeField(blank=False, default=default_time)
    proposal_subs_count = models.PositiveIntegerField(default=1)
    # proposal_postcode = models.CharField(max_length=8)
    proposal_reported = GenericRelation(UserToAdminReportNotAboutUser)

    def save(self, *args, **kwargs):
        # self.proposal_submitter = kwargs['submitter']
        self.proposal_hood = self.proposal_submitter.hood
        self.proposal_postcode = self.proposal_hood.nh_post_code
        self.proposal_slug = slugify("{self.proposal_item_name}-{self.proposal_hood.nh_post_code}-"
                                     "{self.proposal_timestamp}-".format(self=self))
        super(PurchaseProposal, self).save(*args, **kwargs)

    def __str__(self):
        return "this is a proposal to buy : {}".format(self.proposal_item_name)


class CommentToProposal(models.Model):
    comment_text = models.TextField(max_length=MAX_LENGTH_TEXT)
    comment_author = models.ForeignKey(UserProfile, on_delete=models.CASCADE, null=False, related_name="commented")
    comment_subject = models.ForeignKey(PurchaseProposal, on_delete=models.CASCADE, null=False, related_name="comments")
    comment_date = models.DateTimeField(default=default_time)

    class Meta:
        ordering = ['comment_date']

    def __str__(self):
        return f'{self.comment_author} commented on {self.comment_date} : {self.comment_text}'

class UserToUserItemReport(models.Model):
    pass


class UserToAdminReportAboutUser(models.Model):
    pass


class UserProfileReport(UserToAdminReportNotAboutUser):
    pass


class ItemReportToAdmin(UserToAdminReportNotAboutUser):
    pass


class ItemReportToOwner(UserToAdminReportNotAboutUser):
    pass


class GeneralReport(UserToAdminReportNotAboutUser):
    pass


class PurchaseProposalReport(UserToAdminReportNotAboutUser):
    pass
