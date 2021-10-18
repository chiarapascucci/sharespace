
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
    point_value = models.IntegerField(default=1, blank= True)
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
    picture = models.ImageField(upload_to='profile_images', blank=True) #default='profile_images/default.jpg', blank=True)
    user_slug = models.SlugField(unique=True)
    user_post_code = CharField(max_length=8)
    hood = models.ForeignKey(Neighbourhood, on_delete=models.CASCADE) #will need to manage or prevent situation where a neighbourhood is deleted

    def set_hood(self, user_post_code):
        self.hood = Neighbourhood.objects.get_or_create(nh_post_code = user_post_code )[0]
        return self

    def save(self, *args, **kwargs):
        self.user_slug = slugify(self.user.username)
        #self.hood = Neighbourhood.objects.get_or_create(nh_post_code = kwargs['user_post_code'] )[0] #need to check this
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
    price = models.DecimalField(max_digits=10, decimal_places=2)
    main_category = models.ForeignKey(Category, on_delete=models.CASCADE)
    sec_category = models.ForeignKey(Sub_Category, on_delete=models.SET_NULL, null = True)
    available = models.BooleanField(default=True)
    owner = models.ManyToManyField(UserProfile, related_name = "owned", blank = False)
    borrowed_by = models.ForeignKey(UserProfile, related_name = "borrowed", blank = True,  on_delete=models.SET_NULL, null = True)
    item_slug = models.SlugField(unique=True)
    
    max_loan_len = models.PositiveIntegerField(choices=max_len_of_loan_choices, default=1, validators = [MaxValueValidator(4)] )

    def save(self, *args, **kwargs):
        self.id = uuid.uuid4()
        self.item_slug = slugify(self.id)
        print(self.owner)
        super(Item, self).save(*args, **kwargs)
    
class Loan(models.Model):
    requestor = models.OneToOneField(UserProfile, blank = False, on_delete=models.CASCADE)
    item_on_loan = models.OneToOneField(Item, blank = False, on_delete=models.CASCADE)
    overdue = models.BooleanField(default=False)
    out_date = models.DateField(null=False)
    due_date = models.DateField(null=False)
    len_of_loan = models.PositiveIntegerField(default=1, validators = [MaxValueValidator(4)] )
    loan_slug = models.SlugField(unique=True)

    def __str__(self):
        my_str = "{} borrwing {} for {} weeks".format(self.requestor, self.item_on_loan, self.len_of_loan)
        return my_str

    def save(self, *args, **kwargs):
        self.loan_slug = slugify(self.pk)
        self.out_date = datetime.date.today()
        self.due_date = self.out_date.date() + datetime.timedelta(days = 7 * self.len_of_loan)
        print(self)
        super(Loan, self).save(*args, **kwargs)
        print(self)






def upload_gallery_image(instance, filename):
    return f"images/{instance.item.name}/gallery/{filename}"

class Image(models.Model):
    image = models.ImageField(upload_to = upload_gallery_image)
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name = "images")

