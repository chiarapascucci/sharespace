
import uuid
from django.db import models
from django.db.models.deletion import CASCADE
from django.db.models.fields import CharField
from django.db.models.fields.related import ForeignKey, OneToOneField
from django.template.defaultfilters import slugify
from django.contrib.auth.models import User
import datetime
from django.core.validators import MaxValueValidator

MAX_LENGTH_TITLES = 55
MAX_LENGTH_TEXT = 240

class Address(models.Model):
    address_line_1 = models.CharField(max_length = MAX_LENGTH_TITLES, blank = False)
    address_line_2 = models.CharField(max_length = MAX_LENGTH_TITLES, blank = True)
    post_town = models.CharField(max_length = MAX_LENGTH_TITLES, blank = False)
    post_code = CharField(max_length=8, blank = False)
    country = CharField(max_length = MAX_LENGTH_TITLES, default = 'United Kingdom')

class Neighbourhood(models.Model):
    #name = models.CharField(max_length=MAX_LENGTH_TITLES, blank = False)
    nh_post_code = models.CharField(primary_key=True, max_length=8) #need to devise something to enforce valid postcodes
    description = models.CharField(max_length = MAX_LENGTH_TEXT, blank = True)
    nh_slug = models.SlugField()

    def save(self, *args, **kwargs):
        self.nh_slug = slugify(self.nh_post_code)
        super(Neighbourhood, self).save( *args, **kwargs)
    
    def __str__(self):
        return self.nh_post_code

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

class UserProfile(models.Model):
    user = OneToOneField(User, on_delete=models.CASCADE)
    bio = models.CharField(max_length=MAX_LENGTH_TEXT, blank=True)
    picture = models.ImageField(upload_to='profile_images', blank = True, default='profile_images/default_profile_image.png')
    user_slug = models.SlugField(unique=True)
    user_post_code = CharField(max_length=8)
    hood = models.ForeignKey(Neighbourhood, on_delete=models.CASCADE) #will need to manage or prevent situation where a neighbourhood is deleted

    def set_hood(self, user_post_code):
        self.hood = Neighbourhood.objects.get_or_create(nh_post_code = user_post_code)[0]
        return self

    def save(self, *args, **kwargs):
        self.user_slug = slugify(self.user.username)

        super(UserProfile, self).save(*args, **kwargs)

    def __str__(self):
        return self.user.username

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
    max_loan_len = models.PositiveIntegerField(choices=max_len_of_loan_choices, default=1, validators = [MaxValueValidator(4)] )

    def save(self, *args, **kwargs):
        #self.id = uuid.uuid4()
        self.item_slug = slugify(self.id)
        #print(self.owner)
        super(Item, self).save(*args, **kwargs)

    def __str__(self):
        return self.name


def calc_due_date(len_of_loan):
    today = datetime.date.today()
    due_date = today + datetime.timedelta(days = len_of_loan)
    return due_date


class Loan(models.Model):
    requestor = models.OneToOneField(UserProfile, blank = False, related_name = "loans", on_delete=models.CASCADE)
    item_on_loan = models.OneToOneField(Item, blank = False, on_delete=models.CASCADE)
    overdue = models.BooleanField(default=False)
    out_date = models.DateField(auto_now_add = True, null=False)
    due_date = models.DateField(null=False)
    len_of_loan = models.PositiveIntegerField(default=1, validators = [MaxValueValidator(4)] )
    loan_slug = models.SlugField(unique=True)

    def __str__(self):
        my_str = "{} borrowing {} for {} weeks".format(self.requestor, self.item_on_loan, self.len_of_loan)
        return my_str

    def save(self, *args, **kwargs):
        self.loan_slug = slugify("{self.item_on_loan.id}--{self.requestor.user.username}--{self.out_date}".format(self=self))
        self.due_date = calc_due_date(self.len_of_loan)
        super(Loan, self).save(*args, **kwargs)


def upload_gallery_image(instance, filename):
    return f"images/{instance.item.name}/gallery/{filename}"


class Image(models.Model):
    image = models.ImageField(upload_to = upload_gallery_image)
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name = "images")

