import uuid
from django.db import models
from django.db.models.fields.related import OneToOneField
from django.template.defaultfilters import slugify
from django.contrib.auth.models import User


MAX_LENGTH_TITLES = 55
MAX_LENGTH_TEXT = 240

class Neighbourhood(models.Model):
    name = models.CharField(max_length=MAX_LENGTH_TITLES, blank = False)
    post_code = models.CharField(primary_key=True, max_length=7) #need to devise something to enforce valid postcodes
    description = models.CharField(max_length = MAX_LENGTH_TEXT, blank = True)
    slug = models.SlugField(unique=True)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.post_code)
        super(Neighbourhood, self).save(*args, **kwargs)
    
    def __str__(self):
        return self.name

class Category(models.Model):
    name = models.CharField(primary_key=True, max_length=MAX_LENGTH_TITLES)
    description = models.CharField(max_length=MAX_LENGTH_TEXT, blank = True)
    point_value = models.IntegerField(default=1, blank= True)
    slug = models.SlugField(unique=True)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
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
    slug = models.SlugField(unique=True)

    def save(self, *args, **kwargs):
       self.slug = slugify(self.name)
       super(Sub_Category, self).save(*args, **kwargs)

    class Meta:
        verbose_name_plural = 'Secondary Categories'

    def __str__(self):
        return self.name

class UserProfile(models.Model):
    user = OneToOneField(User, on_delete=models.CASCADE)
    bio = models.CharField(max_length=MAX_LENGTH_TEXT, blank=True)
    picture = models.ImageField(upload_to='profile_images', blank=True) #default='profile_images/default.jpg', blank=True)
    slug = models.SlugField(unique=True)
    hood = models.ForeignKey(Neighbourhood, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.user.username)
        super(UserProfile, self).save(*args, **kwargs)

    def __str__(self):
        return self.user.username

class Item(models.Model):
    id = models.UUIDField(primary_key=True, default= uuid.uuid4, editable = False)
    name = models.CharField(max_length=MAX_LENGTH_TITLES)
    description = models.CharField(max_length=MAX_LENGTH_TEXT, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    main_category = models.ForeignKey(Category, on_delete=models.CASCADE)
    sec_category = models.ForeignKey(Sub_Category, on_delete=models.SET_NULL, null = True)
    available = models.BooleanField(default=True)
    owner = models.ManyToManyField(UserProfile, related_name = 'owner')
    borrowed_by = models.ForeignKey(UserProfile, blank = True, on_delete=models.SET_NULL, null = True, related_name = "borrowed")
    slug = models.SlugField(unique=True)

    def save(self, *args, **kwargs):
        self.id = uuid.uuid4()
        self.slug = slugify(self.id)
        super(Item, self).save(*args, **kwargs)

