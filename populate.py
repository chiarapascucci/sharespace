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


def add_item(name, cat, item_owner, address):
    print(item_owner, "line 28")
    print(type(item_owner), "line 29")

    i = Item.objects.get_or_create(name=name, main_category=cat, location=address)[0]
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


def add_user_profile(user,  hood, post_code):

    up = UserProfile.objects.get_or_create(user = user, hood = hood, user_post_code = post_code)[0]
    up.save()
    return up


def populate():

    addresses = {
        1 : {
            'adr_line_1' : 'manor house',
            'post_code' : 'sw96tq',
        },
        2: {
            'adr_line_1': 'fancy villa',
            'post_code': 'sw96tq',
        },
        3: {
            'adr_line_1': 'my house',
            'post_code': 'gl73ay',
        },
        4: {
            'adr_line_1': 'none of your buz',
            'post_code': 'gl73ay',
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


    hoods = ['gl73ay', 'sw96tq']


    #defining add functions for each type

# start with creating the hoods
    '''
     

    for post_code in hoods:
        hood_entity_list.append(add_hood(post_code))
        print(hood_entity_list[-1])
    print("total hoods created: ", len(hood_entity_list))
    '''
    hood_entity_list = []
    address_list = []

    for key, data in addresses.items():
        hood = Neighbourhood.objects.get_or_create(nh_post_code = data['post_code'])[0]
        adr = Address.objects.get_or_create(address_line_1=data['adr_line_1'], adr_hood=hood)[0]
        hood_entity_list.append(hood)
        address_list.append(adr)


# define loops to execute population
# start with creating categories
    cat_list = []
    for cat_name in categories:
        cat_list.append(add_category(cat_name))
        print(cat_list[-1])
    print("total number of categories created: ", len(cat_list))

    # use created categories to create associated sub-categories
    for cat in cat_list:
        sub_cat = sub_categories[cat.name]
        for sc in sub_cat:
            add_sub_cat(sc, cat)
            print(sc)

    user_list = []


    for username, user_data in users.items():
        user = add_user(username, user_data['email'], user_data['password'])
        print("creating user: ", user.username)
        user_list.append(user)

    # user_list.reverse()

    # use created users to create user profiles
    # user profiles creation should automatically create hoods
    user_profile_list = []

    for user in user_list:
        hood = hood_entity_list[random.randint(0, len(hood_entity_list)-1)]
        user_postcode = hood.nh_post_code
        up = add_user_profile(user, hood, user_postcode)
        user_profile_list.append(up)
        print("user profile {} in hood {}".format(up, user_postcode))
    print("total user profile created: ", len(user_profile_list))


# having list of user profiles, categories, and addresses - can now create items
    item_list = []
    for item_name in items:
        owner = user_profile_list[random.randint(0, len(user_profile_list)-1)]
        cat = cat_list[random.randint(0, len(cat_list)-1)]
        poss_hood = owner.hood
        poss_address = Address.objects.filter(adr_hood=poss_hood).first()
        item = add_item(item_name, cat, owner, poss_address)
        item_list.append(item)
        print(item)
    print(len(item_list))

#execution from command line


if __name__ == '__main__':
    print('running po script')
    populate()


