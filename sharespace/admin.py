from django.contrib import admin
from sharespace.models import Item, Category, Sub_Category, UserProfile, Neighbourhood, Image, \
    UserToAdminReportNotAboutUser, UserProfileReport, CustomUser, PurchaseProposal, Loan, Notification


class ImageInLIneAdmin (admin.TabularInline):
    model = Image

class ItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'price', 'main_category', 'sec_category', 'available', )
    fields = ('owner','item_slug', 'name', 'description', 'price', 'main_category', 'sec_category', 'available', 'guardian' )
    prepopulated_fields = {'item_slug': ('name',)}
    inlines = [
        ImageInLIneAdmin
    ]
    model = Item

class NeighbourhoodAdmin(admin.ModelAdmin):
    fields = ('nh_post_code', 'description', 'nh_slug')
    prepopulated_fields = {'nh_slug' :('nh_post_code',)}


class CategoryAdmin (admin.ModelAdmin):
    fields = ('name', 'description', 'point_value', 'cat_slug', 'cat_img')
    prepopulated_fields = {'cat_slug' : ('name',)}


class SubCatAdmin(admin.ModelAdmin):
    fields = ('name', 'description', 'point_value', 'parent', 'sub_cat_slug')
    prepopulated_fields = {'sub_cat_slug' : ('name',)}




admin.site.register(Item, ItemAdmin)
admin.site.register(Neighbourhood, NeighbourhoodAdmin)
admin.site.register(CustomUser)
admin.site.register(UserProfile)
admin.site.register(PurchaseProposal)
admin.site.register(Loan)
admin.site.register(Notification)
admin.site.register(UserToAdminReportNotAboutUser)
admin.site.register(UserProfileReport)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Sub_Category, SubCatAdmin)



# Register your models here.
