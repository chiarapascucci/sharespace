import os
from pprint import pprint

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sharespace_project.settings')

import django
django.setup()
from django.contrib.auth.hashers import PBKDF2PasswordHasher, make_password
from sharespace.models import Item, UserProfile, Category, Sub_Category, Neighbourhood, Address
import random
from sharespace.models import CustomUser as User
from django.core.files import File
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
Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. 
Enim diam vulputate ut pharetra sit. Ullamcorper morbi tincidunt ornare massa.

8.Sport
Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. 
Enim diam vulputate ut pharetra sit. Ullamcorper morbi tincidunt ornare massa.

9.Gardening
Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et 
dolore magna aliqua. Enim diam vulputate ut pharetra sit. Ullamcorper morbi tincidunt ornare massa.

10.Pet Care
Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et 
dolore magna aliqua. Enim diam vulputate ut pharetra sit. Ullamcorper morbi tincidunt ornare massa.

other considered but not included: books, consumables, toy (e.g. board games)
"""