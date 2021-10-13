from django.contrib import admin
from sharespace.models import Item, Category, Sub_Category, UserProfile, Neighbourhood

class ItemAdmin(admin.ModelAdmin):
    fields = ('name', 'description', 'price', 'main_category', 'sec_category', 'available', 'owner', 'item_slug')
    prepopulated_fields = {'item_slug': ('name',)}

class NeighbourhoodAdmin(admin.ModelAdmin):
    fields = ('nh_post_code', 'description', 'nh_slug')
    prepopulated_fields = {'nh_slug' :('nh_post_code',)}


class CategoryAdmin (admin.ModelAdmin):
    fields = ('name', 'description', 'point_value', 'cat_slug')
    prepopulated_fields = {'cat_slug' : ('name',)}


class SubCatAdmin(admin.ModelAdmin):
    fields = ('name', 'description', 'point_value', 'parent', 'sub_cat_slug')
    prepopulated_fields = {'sub_cat_slug' : ('name',)}




admin.site.register(Item, ItemAdmin)
admin.site.register(Neighbourhood, NeighbourhoodAdmin)
admin.site.register(UserProfile)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Sub_Category, SubCatAdmin)


# Register your models here.
