import os
from pprint import pprint

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sharespace_project.settings')

import django
django.setup()
from django.contrib.auth.hashers import PBKDF2PasswordHasher, make_password
from sharespace.models import Item, UserProfile, Category, Sub_Category, Neighbourhood, Address
import random
from django.contrib.auth.models import User
from django.core.files import File
import sharespace_project.settings as Psettings


def add_category(name):
    c = Category.objects.get_or_create(name=name)[0]
    c.save()
    return c


def add_sub_cat(name, category):
    sc = Sub_Category.objects.get_or_create(parent=category, name=name)[0]
    sc.save()
    return sc


def add_item(name, cat, item_owner, address, sub_cat=None):
    print(item_owner, "line 28")
    print(type(item_owner), "line 29")
    i = Item.objects.get_or_create(name=name, main_category=cat, sec_category=sub_cat, location=address)[0]
    i.save()
    i.owner.add(item_owner)
    i.save()
    return i


def add_hood(post_code):
    f_post_code = post_code.strip().lower().replace(' ', '')
    n = Neighbourhood.objects.get_or_create(nh_post_code=f_post_code)[0]
    print(n)
    n.save()
    return n


def add_user(username, email, password):
    user = User.objects.get_or_create(username=username)[0]
    user.email = email
    user.password = make_password(password, salt=None, hasher='default')
    user.save()
    return user


def add_user_profile(user, post_code):
    hood = add_hood(post_code)
    up = UserProfile.objects.get_or_create(user = user, hood = hood, user_post_code = post_code)[0]
    up.save()
    return up


def populate():

    addresses = {
        1 : {
            'adr_line_1' : 'manor house',
            'post_code' : 'ABC 123',
        },
        2: {
            'adr_line_1': 'fancy villa',
            'post_code': 'ABC 543',
        },
        3: {
            'adr_line_1': 'my house',
            'post_code': 'GL7 3AY',
        },
        4: {
            'adr_line_1': 'none of your buz',
            'post_code': 'GL7 3AY',
        }
    }
    #data dictionaries to be populated - manually!! 
    categories = ['kitchen', 'health', 'tech', 'DIY', 'car']

    sub_categories = {
        'kitchen': ['cooking appliances', 'kitchen cleaning', 'baby items'],
        'health' : ['personal health', 'childcare', 'sport'],
        'tech' : ['phone', 'computers and laptops', 'tablets', 'home gadgets'],
        'DIY' : ['painting', 'carpentry', 'restoration', 'art supplies'],
        'car' : ['tires', 'paint', 'tools'],
    }

    items = ['laptop', 'tablet', 'breast pump', 'air pump', 'inflatable mattress', 'chain saw', 'tire pressure metre']

    users =  users = {
       'chp': {'username' : 'chp', 'email':'g1@mail.com', 'password': 'helloyou123'},
       'chpa': {'username' : 'chpa', 'email':'g2@mail.com', 'password': 'helloyou123'},
       'chpas1' : {'username' : 'chpas1', 'email':'g3@mail.com', 'password': 'helloyou123'},
        'chpi': {'username' : 'chpi', 'email':'g4@mail.com', 'password': 'helloyou123'},
        'chpic' : {'username' : 'chpic', 'email':'g5@mail.com', 'password': 'helloyou123'},
    }


    hoods = ['GL7 3AY', 'ABC 233', 'AB24 4HP', 'SW9 6TQ']


    #defining add functions for each type



# define loops to execute population
# start with creating categories
    cat_list = []
    for cat_name in categories:
        cat_list.append(add_category(cat_name))
        print(cat_list[-1])
    print(len(cat_list))

    # use created categories to create associated sub-categories
    for cat in cat_list:
        sub_cat = sub_categories[cat.name]
        for sc in sub_cat:
            add_sub_cat(sc, cat)
            print(sc)

    user_list = []
    hood_list = []

    for username, user_data in users.items():
        user = add_user(username, user_data['email'], user_data['password'])
        print("creating: ", user.username)
        user_list.append(user)

    # user_list.reverse()

    # use created users to create user profiles
    # user profiles creation should automatically create hoods
    user_profile_list = []

    for user in user_list:
        hood = hoods[random.randint(0, 3)]
        print(hood)
        up = add_user_profile(user, hood)
        hood_list.append(up.hood)
        user_profile_list.append(up)
        print(up)
    print(len(user_profile_list))

# create addresses (placeholders to create objects)
    address_list=[]
    for key, data in addresses.items():
        adr = Address.objects.get_or_create(address_line_1 = data['adr_line_1'],
                                            adr_hood = hood_list[random.randint(0, len(hood_list)-1)])[0]
        address_list.append(adr)
        pprint(adr)
        print(type(adr))

# create user


# having list of user profiles and categories - can now create items
    item_list = []
    for item_name in items:
        owner = user_profile_list[random.randint(0, len(user_profile_list)-1)]
        cat = cat_list[random.randint(0, len(cat_list)-1)]
        address = address_list[random.randint(0, 3)]
        item = add_item(item_name, cat, owner, address)
        item_list.append(item)
        print(item)
    print(len(item_list))

#execution from command line


if __name__ == '__main__':
    print('running po script')
    populate()


