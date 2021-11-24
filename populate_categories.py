import os
from pprint import pprint

from sharespace.text_data import get_placeholder

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sharespace_project.settings')

import django
django.setup()
from sharespace.models import Category, Sub_Category
import sharespace_project.settings as Psettings

"""
1.Kitchen
This category should contain all items that you may find, or wish to find, in your kitchen. From special cooking utensils to small appliances. 
If your item has some to do with all that happens in your kitchen this is the right category for it - remember to have a look the more
specific categories under Kitchen

2.Cleaning
We all know how much of a hassle keep your house clean it can be. But every now and then we do find that gadget that makes work
a little bit easier. If you are looking to share this type of great finds with your neighbours this is the right category. 
Help your neighbours even more and select the right sub-category... what can you clean with this item?

3.Technology
This category can feel a bit broad, but under here you should place all things techy! Got a spare laptop that you do not mind lending out
for a wee while? A spare PS4 controller? A tablet? All the "essential" gadgets of the new digital age

4.Health & Beauty
We all need to look after our wellbeing. There are tons of way to do this: meditate, go for a walk, have a cuppa with a friend...
Or maybe you want to use your new yoga mat that has been sitting in the corner for months? Or your new and untouched kettle bell set?
That's great, why not also share those with your neighbours when you are done? Maybe you'll find your next asynch workout buddy

5.Childcare
Looking after some little ones is an incredibly rewarding but challenging experience. Especially if you are not fully geared up!
So if you happened to find the perfect crib, but your child has now grown just too restless for it, why not share that with your next door neighbour?


6.DIY & Home Improvement
Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. 
Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.

7.Garage


8.Sport


9.Gardening


10.Pet Care

other considered but not included: books, consumables, toy (e.g. board games)
"""

default_desc = get_placeholder()

main_categories_data = {
    'Kitchen' : {'name': "Kitchen",
                 'description': """"This category should contain all items that you may find, or wish to find, in your kitchen. From special cooking utensils to small appliances.  If your item has some to do with all that happens in your kitchen this is the right category for it - remember to have a look the more specific categories under Kitchen""",
                 'pic': "https://openclipart.org/download/308235/1539607597.svg"},

    'Cleaning' : {'name': "Cleaning",
                  'description': """"We all know how much of a hassle keep your house clean it can be. But every now and then we do find that gadget that makes work a little bit easier. If you are looking to share this type of great finds with your neighbours this is the right category. Help your neighbours even more and select the right sub-category... what can you clean with this item?""",
                  'pic': "https://p2.piqsels.com/preview/714/609/274/clean-rag-cleaning-rags-budget.jpg"},

    'Technology' : {'name' : 'Technology',
                    'description':"""This category can feel a bit broad, but under here you should place all things techy! Got a spare laptop that you do not mind lending out for a wee while? A spare PS4 controller? A tablet? All the "essential" gadgets of the new digital age""",
                    'pic':'https://p1.pxfuel.com/preview/799/347/679/gadgets-technology-laptop-mobile-phone-business-electronic.jpg'},

    'Health & Beauty' : {'name': 'Health & Beauty',
                         'description':"""We all need to look after our wellbeing. There are tons of way to do this: meditate, go for a walk, have a cuppa with a friend...Or maybe you want to use your new yoga mat that has been sitting in the corner for months? Or your new and untouched kettle bell set? That's great, why not also share those with your neighbours when you are done? Maybe you'll find your next asynch workout buddy""",
                         'pic':'https://p0.piqsels.com/preview/162/277/152/flatlay-medical-toys-health.jpg'},

    'Childcare': {'name' : 'Childcare',
                  'description': """Looking after some little ones is an incredibly rewarding but challenging experience. Especially if you are not fully geared up! So if you happened to find the perfect crib, but your child has now grown just too restless for it, why not share that with your next door neighbour?""",
                  'pic':'https://p0.piqsels.com/preview/63/988/932/multicolored-learning-toys.jpg'},

    'DIY & Home Improvement' : {'name': 'DIY & Home Improvement',
                                'description': default_desc,
                                'pic':'https://p0.piqsels.com/preview/74/701/282/textures-flatlay-craft-diy-sewing.jpg'},

    'Garage' : {'name': 'Garage',
                'description': default_desc,
                 'pic':'https://p0.piqsels.com/preview/703/612/852/various-car-car-wash-cars.jpg'},

    'Sport' : {'name': 'Sport',
               'description': default_desc,
               'pic':'https://p2.piqsels.com/preview/12/998/321/grey-sport-shoes-sneakers.jpg'},

    'Gardening': {'name': 'Gardening',
              'description': default_desc,
              'pic': 'https://p2.piqsels.com/preview/297/325/90/garden-plants-spring-hoe.jpg'},

    'Pet Care': {'name': 'Pet Care',
              'description': default_desc,
              'pic': 'https://p0.piqsels.com/preview/731/992/56/dog-pet-animal-cute.jpg'},
}

sec_cat= {
    'Kitchen' : ['utensils', 'cookware', 'baking', 'appliances'],
    'Cleaning': ['bathroom cleaning', 'carpet', 'stains', 'upholstery', 'curtains', 'deep cleaning', 'kitchen cleaning'],
    'Technology': ['laptop', 'tablet', 'PC', 'screens', 'cables and wires', 'gaming', 'music', 'video recording'],
    'Health & Beauty': ['blood pressure and heart', 'make-up', 'skincare',  'breathing', 'hair care', 'shaving and waxing'],
    'Childcare' : ['feeding', 'breast feeding', 'toys', 'sleeping', 'bathing', 'cribs', 'other gadgets'],
    'DIY & Home Improvement' : ['tools', 'painting', 'wall repair', 'ceiling repair', 'floor repair', 'tiling', 'carpet repair', 'carpentry', 'metal working'],
    'Garage' : ['air pump', 'tire pressure', 'car engine', 'spare parts'],
    'Sport' : ['winter sports', 'cycling', 'home workout', 'running', 'water sports', 'gym', 'other outdoor activities' ],
    'Gardening' : ['potting', 'planting', 'sowing', 'plant cutting', 'irrigation', 'plant care'],
    'Pet Care' : ['pet beds', 'pet toys', 'pet food', 'pet health', 'pet walking', 'pet training', 'pet activity'],

}

def create_categories():
    cats_dict = {}
    cat_list = []


    for cat, cat_data in main_categories_data.items():
        category = Category.objects.create(name = cat, description=cat_data['description'], cat_img=cat_data['pic'])
        cat_list.append(category)
        print(f"category created: {category}, its sub categories are: ")
        sub_cat_list = []
        sub_cat_list_names = sec_cat[cat]
        for sc in sub_cat_list_names:
            sub_category = Sub_Category.objects.create(name = sc, description = default_desc, parent=category)
            sub_cat_list.append(sub_category)
            print(f" - {sub_category}")
        cats_dict[f'{cat}'] = sub_cat_list

    return cats_dict


