from django.contrib import admin
from sharespace.models import Item, Category, Sub_Category, UserProfile, Neighbourhood

class ItemAdmin(admin.ModelAdmin):
    fields = ('name', 'description', 'price', 'main_category', 'sec_category', 'available', 'owner')
    prepopulated_fields = {'slug': ('name',)}

class NeighbourhoodAdmin(admin.ModelAdmin):
    fields = ('name', 'post_code', 'description')
    prepopulated_fields = {'slug' :('post_code',)}


class CategoryAdmin (admin.ModelAdmin):
    fields = ('name', 'description', 'point_value')
    prepopulated_fields = {'slug' : ('name',)}


class SubCatAdmin(admin.ModelAdmin):
    fields = ('name', 'description', 'point_value', 'parent')
    prepopulated_fields = {'slug' : ('name',)}




admin.site.register(Item, ItemAdmin)
admin.site.register(Neighbourhood, NeighbourhoodAdmin)
admin.site.register(UserProfile)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Sub_Category, SubCatAdmin)


# Register your models here.
