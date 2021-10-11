import os 

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sharespace_project')

import django
django.setup()
from django.contrib.auth.hashers import PBKDF2PasswordHasher, make_password
from sharespace.models import Item, User, UserProfile, Category, Sub_Category, Neighbourhood

def populate():

    #data dictionaries to be populated - manually!! 
    categories = []

    sub_categories = []

    items = []

    users = []

    user_profiles = []

    neighbourhoods = []


    #defining add functions for each type

    def add_category(name, point_value):
        c = Category.objects.get_or_create(name = name)[0]
        c.point_value = point_value
        c.save
        return c

    def add_sub_cat(name, category):
        sc = Sub_Category.objects.get_or_create(parent = category, name = name)[0]
        sc.save()
        return sc
    
    def add_item (name, price, cat, owner, sub_cat = None):
        i = Item.objects.get_or_create(name = name, price = price, main_category = cat, sec_category = sub_cat, owner = owner)
        i.save()
        return i 

    def add_neighbourhood(post_code, name):
        n = Neighbourhood.objects.get_or_create(post_code = post_code)[0]
        n.name = name
        n.save()
        return n

    def add_user(username, email, password):
        user = User.objects.get_or_create(username=username)[0]
        user.email = email
        user.password = make_password(password, salt=None, hasher='default')
        user.save()
        return user

    def add_user_profile(user, hood):
      up = UserProfile.objects.get_or_create(user = user, hood = hood)[0]
      up.save()
      return up  

# define loops to execute population


#execution from command line
if __name__ == '__main__':
    print ('running po script')
    populate()