
import uuid

from django.contrib.auth.base_user import BaseUserManager, AbstractBaseUser
from django.db import models

from django.db.models.fields import CharField
from django.db.models.fields.related import ForeignKey, OneToOneField
from django.template.defaultfilters import slugify
from django.contrib.auth.models import PermissionsMixin
from datetime import datetime, date, time, timedelta, timezone

from django.core.validators import MaxValueValidator

MAX_LENGTH_TITLES = 55
MAX_LENGTH_TEXT = 240


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
    address_line_1 = models.CharField(max_length = MAX_LENGTH_TITLES, blank = False)
    address_line_2 = models.CharField(max_length = MAX_LENGTH_TITLES, default = '')
    address_line_3 = models.CharField(max_length = MAX_LENGTH_TITLES, default = '')
    address_line_4 = models.CharField(max_length=MAX_LENGTH_TITLES, default = '')
    locality = models.CharField(max_length=MAX_LENGTH_TITLES, default='')
    city = models.CharField(max_length = MAX_LENGTH_TITLES, default = '')
    county = models.CharField(max_length=MAX_LENGTH_TITLES, default = '')
    country = models.CharField(max_length = MAX_LENGTH_TITLES, default = 'United Kingdom')

    adr_hood = models.ForeignKey(Neighbourhood, blank = False, on_delete = models.CASCADE)

    def __str__(self):
        address_str = self.address_line_1 + "\n" + self.address_line_2 + "\n" + self.city + "\n" + self.adr_hood.nh_post_code
        return address_str


class Category(models.Model):
    name = models.CharField(primary_key=True, max_length=MAX_LENGTH_TITLES)
    description = models.CharField(max_length=MAX_LENGTH_TEXT, blank = True)
    point_value = models.IntegerField(default=1)
    cat_slug = models.SlugField(unique=True)

    def save(self, *args, **kwargs):
        self.cat_slug = slugify(self.name)
        super(Category, self).save(*args, **kwargs)

    class Meta:
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name


class Sub_Category(models.Model):
    name = models.CharField(primary_key=True, max_length=MAX_LENGTH_TITLES)
    description = models.CharField(max_length=MAX_LENGTH_TEXT)
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

class UserManager(BaseUserManager):
    def _create_user(self, username, email, password, is_staff, is_superuser, **extra_fields):
        if not email:
            raise ValueError('Users must have an email address')
        now = datetime.now()
        email = self.normalize_email(email)
        user = self.model(
            username = username,
            email=email,
            is_staff=is_staff,
            is_active=True,
            is_superuser=is_superuser,
            last_login=now,
            date_joined=now,
            **extra_fields
        )
        user.set_password(password)
        if not is_superuser:
            print("in user manager model")
            user.create_linked_profile(extra_fields['bio'], extra_fields['picture'], extra_fields['user_post_code'])
        user.save(using=self._db)
        return user

    def create_user(self, username, email, password, **extra_fields):
        return self._create_user(username, email, password, False, False, **extra_fields)

    def create_superuser(self, username, email, password, **extra_fields):
        user = self._create_user(username, email, password, True, True, **extra_fields)
        user.save(using=self._db)
        return user

class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(max_length=254, unique=True)
    username = models.CharField(max_length=MAX_LENGTH_TITLES, blank = False, unique=True)
    first_name = models.CharField(max_length=254, null=True, blank=True)
    last_name = models.CharField(max_length=254, null=True, blank=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    last_login = models.DateTimeField(null=True, blank=True)
    date_joined = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'username'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = [EMAIL_FIELD,]

    objects = UserManager()

    def create_linked_profile(self, bio, picture, user_post_code):
        UserProfile.objects.create(user = self, bio = bio, picture = picture, user_post_code = user_post_code)

    def get_absolute_url(self):
        return "/users/%i/" % (self.pk)

class UserProfile(models.Model):
    user = OneToOneField(User, on_delete=models.CASCADE, related_name='userinfo')
    bio = models.CharField(max_length=MAX_LENGTH_TEXT, blank=True)
    picture = models.ImageField(upload_to='profile_images', blank = True, default='profile_images/default_profile_image.png')
    user_slug = models.SlugField(unique=True)
    user_post_code = CharField(max_length=8)
    max_no_of_items = models.PositiveIntegerField(default = 1)
    curr_no_of_items = models.PositiveIntegerField(default = 0)
    can_borrow = models.BooleanField(default = True)
    hood = models.ForeignKey(Neighbourhood, on_delete=models.CASCADE) #will need to manage or prevent situation where a neighbourhood is deleted

    def set_hood(self, user_post_code):
        f_user_post_code = user_post_code.strip().replace(' ','').lower()
        self.hood = Neighbourhood.objects.get_or_create(nh_post_code = f_user_post_code)[0]
        return self

    def save(self, *args, **kwargs):
        self.user_slug = slugify(self.user.username)
        self.user_post_code = self.user_post_code.strip().replace(' ','').lower()
        print("curr no of items" , self.curr_no_of_items)
        if self.curr_no_of_items >= self.max_no_of_items:
            self.can_borrow = False
        else:
            self.can_borrow = True
            print(self.can_borrow)
        super(UserProfile, self).save(*args, **kwargs)

    def __str__(self):
        return self.user.username





class HoodGroup(models.Model):
    group_name = models.CharField(blank = False, null=False, max_length=MAX_LENGTH_TITLES, primary_key=True)
    group_description = models.TextField(blank = True, max_length=MAX_LENGTH_TEXT)
    group_founder = models.ForeignKey(UserProfile, null=False, on_delete=models.CASCADE, related_name = 'founded')
    group_members = models.ManyToManyField(UserProfile, blank=True, related_name = 'member_of')
    group_hood = models.ForeignKey(Neighbourhood, blank = False, null = False, on_delete=models.CASCADE)
    group_slug = models.SlugField(null = False)

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
    id = models.UUIDField(primary_key=True, default= uuid.uuid4, editable = False)
    name = models.CharField(max_length=MAX_LENGTH_TITLES)
    description = models.CharField(max_length=MAX_LENGTH_TEXT, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default = 10.00)
    main_category = models.ForeignKey(Category, on_delete=models.CASCADE)
    sec_category = models.ForeignKey(Sub_Category, on_delete=models.SET_NULL, null = True)
    available = models.BooleanField(default=True)
    owner = models.ManyToManyField(UserProfile, related_name = "owned", blank = False)
    borrowed_by = models.ForeignKey(UserProfile, related_name = "borrowed", blank = True,  on_delete=models.SET_NULL, null = True)
    item_slug = models.SlugField(unique=True)
    location = models.ForeignKey(Address, on_delete = models.CASCADE, blank = False)
    max_loan_len = models.PositiveIntegerField(choices=max_len_of_loan_choices, default=4, validators = [MaxValueValidator(4)] )
    item_post_code = CharField(max_length=8)

    def save(self, *args, **kwargs):
        #self.id = uuid.uuid4()
        self.item_slug = slugify(self.id)
        #print(self.owner)
        self.item_post_code = self.location.adr_hood.nh_post_code
        super(Item, self).save(*args, **kwargs)

    def __str__(self):
        return self.name





class Loan(models.Model):
    id = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    requestor = models.ForeignKey(UserProfile, blank = False, related_name = "loans", on_delete=models.CASCADE)
    item_on_loan = models.ForeignKey(Item, blank = False, on_delete=models.CASCADE)
    overdue = models.BooleanField(default=False)
    active = models.BooleanField(default = True)
    out_date = models.DateTimeField(null=False)
    due_date = models.DateTimeField(null=True)
    len_of_loan = models.PositiveIntegerField(default=1, validators = [MaxValueValidator(4)] )
    loan_slug = models.SlugField(primary_key=True)

    def __str__(self):
        my_str = "{} borrowing {} for {} weeks".format(self.requestor, self.item_on_loan, self.len_of_loan)
        return my_str

    def save(self, *args, **kwargs):
        self.loan_slug = slugify(
            "{self.requestor.user.username}-loan-{self.id}".format(self=self))
        print("\n in save method in loan model \n out time: {} \n due time: {} ".format(self.out_date, self.due_date))
        super(Loan, self).save(*args, **kwargs)

    def apply_loan(self, len_of_loan):
        # setting loan's due date
        due_date = self.out_date + timedelta(days=(len_of_loan * 7))
        self.due_date = due_date
        self.save()

        # updating requestor's status
        self.requestor.curr_no_of_items = self.requestor.curr_no_of_items + 1
        if self.requestor.curr_no_of_items >= self.requestor.max_no_of_items:
            self.requestor.can_borrow = False
            self.requestor.save()
        else:
            self.requestor.save()

        # updating item's status
        self.item_on_loan.available = False
        self.item_on_loan.save()

    def mark_as_complete(self):
        self.active = False
        self.item_on_loan.available = True
        self.item_on_loan.save()
        self.requestor.curr_no_of_items = self.requestor.curr_no_of_items -1
        if self.requestor.curr_no_of_items < self.requestor.max_no_of_items:
            self.requestor.can_borrow = True
            self.requestor.save()
        self.save()


def upload_gallery_image(instance, filename):
    return f"images/{instance.item.name}/gallery/{filename}"


class Image(models.Model):
    image = models.ImageField(upload_to = upload_gallery_image)
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name = "images")


class PurchaseProposal(models.Model):
    submitter = models.ForeignKey(UserProfile, blank=False, on_delete=models.CASCADE, related_name="proposals")
    subscribers = models.ManyToManyField(UserProfile, blank=True, related_name="interested")
    item_name = models.TextField(blank=False, max_length=MAX_LENGTH_TITLES)
    item_description = models.TextField(blank= False, max_length=MAX_LENGTH_TEXT)
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=False)
    location = models.ForeignKey(Address, on_delete=models.CASCADE)
    proposal_slug = models.SlugField(primary_key=True)
    active = models.BooleanField(default = True)
    purchased = models.BooleanField(default = False)
    timestamp = models.DateTimeField(blank=False)
    proposal_postcode = models.CharField(max_length=8)

    def save(self, *args, **kwargs):
        self.timestamp = datetime.now()
        self.proposal_postcode = self.location.adr_hood.nh_post_code
        self.proposal_slug = slugify("{self.item_name}-{self.proposal_postcode}-{self.timestamp}-".format(self=self))