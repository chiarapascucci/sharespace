import os
from pprint import pprint

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sharespace_project.settings')

import django
django.setup()
from django.contrib.auth.hashers import PBKDF2PasswordHasher, make_password
from sharespace.models import Item, UserProfile, Category, Sub_Category, Neighbourhood, Address, Notification, \
    PurchaseProposal
import random
from sharespace.models import CustomUser as User
from django.core.files import File
import sharespace_project.settings as Psettings
from populate_categories import create_categories


def add_category(name):
    c = Category.objects.get_or_create(name=name)[0]
    c.save()
    return c


def add_sub_cat(name, category):
    sc = Sub_Category.objects.get_or_create(parent=category, name=name)[0]
    sc.save()
    return sc


def add_item(name, cat, sub_cat, item_owner, address):
    i = Item.objects.get_or_create(name=name, main_category=cat, sec_category = sub_cat, location=address, guardian=item_owner)[0]
    i.owner.add(item_owner)
    i.save()
    print("creating item - populate - log: ", i)
    return i


def add_hood(post_code):
    f_post_code = post_code.strip().lower().replace(' ', '')
    n = Neighbourhood.objects.get_or_create(nh_post_code=f_post_code)[0]
    print(n)
    n.save()
    return n


def add_user(username, email, password):
    user = User.objects.get_or_create(username=username, email=email)[0]
    user.password = make_password(password, salt=None, hasher='default')
    user.save()
    return user


def add_user_profile(user,  hood, post_code, contact):
    up = UserProfile.objects.get_or_create(user = user, hood = hood, user_post_code = post_code, contact_details=contact)[0]
    up.save()
    return up


def get_cat_sub_cat():
    cat = Category.objects.order_by('?').first()
    sub_cat = Sub_Category.objects.filter(parent=cat).first()
    return [cat, sub_cat]


def add_purchase_proposal(name, description, price, submitter, subs):
    cat_sub_cat = get_cat_sub_cat()
    cat = cat_sub_cat[0]
    sub_cat = cat_sub_cat[1]

    contact = submitter.contact_details
    pp = PurchaseProposal.objects.get_or_create(proposal_submitter=submitter, proposal_contact=contact,
                                                proposal_item_name=name, proposal_item_description=description,
                                                proposal_cat=cat, proposal_sub_cat=sub_cat, proposal_price=price)[0]
    print("purchase proposal created: ", pp)
    for s in subs:
        pp.proposal_subscribers.add(s)
        pp.proposal_subs_count += 1

    pp.save()
    return pp


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
    }

    items_dict = {
    'Kitchen' : {'utensils':['egg beater', 'italian coffee machine'],
                 'cookware':['50L pot', 'rice cooker', 'wok pan'],
                 'baking':['stem mixer', 'prooving box', 'bread machine'],
                 'appliances':['microwave', 'gas fire lamp', 'electric oven']},
    'Cleaning': {'bathroom cleaning': ['mop', 'anti-limescale liquid', 'toilet brush', 'bleach'],
                 'carpet':['capert cleaner machine', 'eletric carpet cleaner', 'powerful carpet vacuum cleaner'],
                 'stains':['stain removal product', 'stain removal brush', 'ink stain removal liquid', 'pre-wash stain removal'],
                 'upholstery' :['hand vacuum cleaner', 'stain removal for sofas', 'anti-oudour spray', 'sofa leather care product'],
                 'curtains' : ['curtain iron', 'curtain steamer', 'duster for curtains'],
                 'deep cleaning': ['steam cleaner', 'water pressure cleaner', 'anti-mould spray', 'anti-mould product'],
                 'kitchen cleaning': ['mop', 'kitchen sanitising product'] },
    'Technology': {'laptop': ['mouse with wire', 'wireless mouse', 'wired keyboard', 'wireless keyboard', 'drawing trackpad', 'mouse pad'],
                   'tablet' : ['tablet cleaning cloth and spray', 'apple tablet charger', 'tablet charger', 'tablet cover', 'tablet stand'],
                   'PC': ['pressurised air can', 'mouse', 'wireless mouse', 'cd reader', 'headset', 'gaming chair', 'audio system'],
                    'screens': ['15'' screen', '40 inches screen', '10 inches screen', 'curved screen'],
                   'cables and wires':['hdmi cable', 'hdmi', 'usb to usb cable', 'apple adaptor'],
                   'gaming' : ['gaming seat', 'gaming headset', 'gaming keyboard'],
                   'music' : ['wireless stereo', 'bluetooth music box'],
                   'video recording': ['tape video camera', 'digital camera', 'go pro camera']},
    'Health & Beauty': {'blood pressure and heart':['blood pressure measure', 'manual blood pressure pump', 'eletronic blood pressure meter'],
                        'make-up':['vanity mirror', 'professional brush set'],
                        'skincare':['steam facial machine', 'fake tan set', ],
                        'breathing':['placeholder_item_1', 'placeholder_item_2', 'placeholder_item_3'],
                        'hair care':['placeholder_item_1', 'placeholder_item_2', 'placeholder_item_3'],
                        'shaving and waxing':['placeholder_item_1', 'placeholder_item_2', 'placeholder_item_3']},
    'Childcare' : {'feeding': ['placeholder_item_1', 'placeholder_item_2', 'placeholder_item_3'],
                   'breast feeding': ['placeholder_item_1', 'placeholder_item_2', 'placeholder_item_3'],
                   'toys' : ['placeholder_item_1', 'placeholder_item_2', 'placeholder_item_3'],
                   'sleeping' : ['placeholder_item_1', 'placeholder_item_2', 'placeholder_item_3'],
                   'bathing' : ['placeholder_item_1', 'placeholder_item_2', 'placeholder_item_3'],
                   'cribs' : ['placeholder_item_1', 'placeholder_item_2', 'placeholder_item_3'],
                   'other gadgets' : ['placeholder_item_1', 'placeholder_item_2', 'placeholder_item_3']},
    'DIY & Home Improvement' : {'tools' :['placeholder_item_1', 'placeholder_item_2', 'placeholder_item_3'],
                                'painting':['placeholder_item_1', 'placeholder_item_2', 'placeholder_item_3'],
                                'wall repair':['placeholder_item_1', 'placeholder_item_2', 'placeholder_item_3'],
                                'ceiling repair':['placeholder_item_1', 'placeholder_item_2', 'placeholder_item_3'],
                                'floor repair':['placeholder_item_1', 'placeholder_item_2', 'placeholder_item_3'],
                                'tiling':['placeholder_item_1', 'placeholder_item_2', 'placeholder_item_3'],
                                'carpet repair':['placeholder_item_1', 'placeholder_item_2', 'placeholder_item_3'],
                                'carpentry':['placeholder_item_1', 'placeholder_item_2', 'placeholder_item_3'],
                                'metal working':['placeholder_item_1', 'placeholder_item_2', 'placeholder_item_3']},
    'Garage' : {'air pump' :['placeholder_item_1', 'placeholder_item_2', 'placeholder_item_3'],
                'tire pressure':['placeholder_item_1', 'placeholder_item_2', 'placeholder_item_3'],
                'car engine' :['placeholder_item_1', 'placeholder_item_2', 'placeholder_item_3'],
                'spare parts':['placeholder_item_1', 'placeholder_item_2', 'placeholder_item_3']},
    'Sport' : {'winter sports' :['placeholder_item_1', 'placeholder_item_2', 'placeholder_item_3'],
               'cycling' :['placeholder_item_1', 'placeholder_item_2', 'placeholder_item_3'],
               'home workout' :['placeholder_item_1', 'placeholder_item_2', 'placeholder_item_3'],
               'running':['placeholder_item_1', 'placeholder_item_2', 'placeholder_item_3'],
               'water sports':['placeholder_item_1', 'placeholder_item_2', 'placeholder_item_3'],
               'gym' :['placeholder_item_1', 'placeholder_item_2', 'placeholder_item_3'],
               'other outdoor activities' :['placeholder_item_1', 'placeholder_item_2', 'placeholder_item_3']},
    'Gardening' : {'potting' :['placeholder_item_1', 'placeholder_item_2', 'placeholder_item_3'],
                   'planting' :['placeholder_item_1', 'placeholder_item_2', 'placeholder_item_3'],
                   'sowing' :['placeholder_item_1', 'placeholder_item_2', 'placeholder_item_3'],
                   'plant cutting' :['placeholder_item_1', 'placeholder_item_2', 'placeholder_item_3'],
                   'irrigation' :['placeholder_item_1', 'placeholder_item_2', 'placeholder_item_3'],
                   'plant care' :['placeholder_item_1', 'placeholder_item_2', 'placeholder_item_3']},
    'Pet Care' : {'pet beds' :['placeholder_item_1', 'placeholder_item_2', 'placeholder_item_3'],
                  'pet toys' :['placeholder_item_1', 'placeholder_item_2', 'placeholder_item_3'],
                  'pet food' :['placeholder_item_1', 'placeholder_item_2', 'placeholder_item_3'],
                  'pet health':['placeholder_item_1', 'placeholder_item_2', 'placeholder_item_3'],
                  'pet walking':['placeholder_item_1', 'placeholder_item_2', 'placeholder_item_3'],
                  'pet training':['placeholder_item_1', 'placeholder_item_2', 'placeholder_item_3'],
                  'pet activity':['placeholder_item_1', 'placeholder_item_2', 'placeholder_item_3']},
    }



    users = {
       'chp': {'username' : 'chp', 'email':'g1@mail.com', 'password': 'helloyou123', 'contact': '+4407743562738'},
       'chpa': {'username' : 'chpa', 'email':'GG2@mail.com', 'password': 'helloyou123', 'contact': '+4407743562739'},
       'chpas1' : {'username' : 'chpas1', 'email':'g3@mail.com', 'password': 'helloyou123', 'contact': '+4407743562731'},
        'chpi': {'username' : 'chpi', 'email':'gG4@mail.com', 'password': 'helloyou123', 'contact': '+4407743562732'},
        'chpic' : {'username' : 'chpic', 'email':'g5@MAIL.com', 'password': 'helloyou123', 'contact': '+4407743562733'},
    }

    contact_list = ['+4407743562738', '+4407743562739', '+4407743562731', '+4407743562732', '+4407743562733']

    hoods = ['sw96tq']


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


    cat_dict = create_categories()



    user_list = []


    for username, user_data in users.items():
        user = add_user(username, user_data['email'], user_data['password'])
        print("creating user: ", user.username)
        user_list.append(user)

    # user_list.reverse()

    # use created users to create user profiles
    # user profiles creation should automatically create hoods
    user_profile_list = []
    assert (len(user_list) == len(contact_list))
    for i in range(0, len(user_list)):
        hood = hood_entity_list[random.randint(0, len(hood_entity_list)-1)]
        user_postcode = hood.nh_post_code
        up = add_user_profile(user_list[i], hood, user_postcode, contact_list[i])
        user_profile_list.append(up)
        print("user profile {} in hood {}".format(up, user_postcode))
    print("total user profile created: ", len(user_profile_list))


# having list of user profiles, categories, and addresses - can now create items
    item_list = []
    for k,v in items_dict.items():
        cat = Category.objects.get(name=k)
        sub_cat_dict = v
        for key,val in sub_cat_dict.items():
            sub_cat= Sub_Category.objects.get(name=key)

            for item_name in val:
                owner = user_profile_list[random.randint(0, len(user_profile_list)-1)]
                poss_hood = owner.hood
                poss_address = Address.objects.filter(adr_hood=poss_hood).first()
                item = add_item(item_name, cat, sub_cat, owner, poss_address)
                item_list.append(item)

    print(len(item_list))

    purchase_proposals = [
        ['cement mixer', 'machine to mix cement', 2500],
        ['outdoor gym', 'jungle gym for kids to play in', 10000],
        ['pool', 'large inflatable pool perfect for summer', 800],
        ['hotub', 'inflatable hotub both cold and warm water', 970.50],
        ['tanning bed', 'we could store this somewhere and all get tanned', 15000],
        ['car', 'anyone up for car sharing?', 4600],
        ['event marquee', 'would be cool to have a marque for any event in our neighbourhood', 5700]
    ]
    for i in range(0, len(purchase_proposals)):
        r = random.randint(0, len(user_profile_list)-1)
        up = user_profile_list[r]
        up_set = set(user_profile_list)
        up_set.remove(up)
        pp = add_purchase_proposal(purchase_proposals[i][0], purchase_proposals[i][1], purchase_proposals[i][2], up, up_set)






# deleting all notifications
    Notification.objects.all().delete()


if __name__ == '__main__':
    print('running po script')

    populate()


