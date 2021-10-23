from django.urls import path 
from sharespace import views
from sharespace.views import BorrowItemView

app_name = 'sharespace'

urlpatterns = [
    path('', views.index, name='index'),
    path('about/', views.about_view, name = 'about'),
    path('register/', views.register_view, name = 'register_profile'),
    path('register/address', views.address_lookup_view, name = 'address_lookup'),
    path('login/', views.login, name = 'login'),
    path('change_password/', views.change_password_view, name = 'change_password'),

    path('category/', views.category_list_view, name = 'category_list'),
    path('category/<slug:cat_slug>/', views.category_page_view, name = 'category_page'),
    path('category/<slug:cat_slug>/<slug:sub_cat_slug>/', views.sub_cat_page_view, name = 'sub_cat_page'),

    path('item/', views.item_list_view, name = 'item_list'),
    path('add_item/', views.add_item_view, name = 'add_item'),
    path('item/<slug:item_slug>/', views.item_page_view, name = 'item_page'),
    path('item/<slug:item_slug>/borrow/', BorrowItemView.as_view(), name='borrow_item'),

    path('user/<slug:user_slug>/', views.user_profile_view, name='user_profile'),
    path('user/<slug:user_slug>/edit/', views.edit_user_view, name = 'edit_user_info'),

    path('ajax/load_sub_cat', views.load_sub_cat_view, name = "ajax_load_sub_cat"),
]
