from django.urls import path 
from sharespace import views
from sharespace.views import BorrowItemView

app_name = 'sharespace'

urlpatterns = [
    path('', views.index, name='index'),
    path('about/', views.about, name = 'about'),
    path('register/', views.register, name = 'register_profile'),
    path('add_item/', views.add_item, name = 'add_item'),
    path('item/', views.item_list_view, name = 'item_list'),
    path('<slug:item_slug>/', views.item_page_view, name = 'item_page'), #forward slash?
    path('<slug:item_slug>/borrow/', BorrowItemView.as_view(), name='borrow_item'),
    path('category/', views.category_list, name = 'category_list'),
    path('category/<slug:cat_slug>/', views.category_page, name = 'category_page'),
    path('category/<slug:cat_slug>/<slug:sub_cat_slug>/', views.sub_cat_page, name = 'sub_cat_page'),
    path('<slug:user_slug>/', views.user_profile_view, name = 'user_profile'),
    path('<slug:user_slug>/edit/', views.edit_user, name = 'edit_user_info'),



    path('login/', views.login, name = 'login'),

]
