from django import forms
from django.forms.widgets import EmailInput 
from sharespace.models import Item, Neighbourhood, User, UserProfile

class UserForm(forms.ModelForm):
    password = forms.CharField(widget = forms.PasswordInput())
    email = forms.EmailField(widget = forms.EmailInput())

    class Meta:
        fields = ('email', 'password', 'username')
        model = User

class UserProfileForm(forms.ModelForm):
    class Meta:
        fields = ('bio', 'picture', 'user_post_code')
        model = UserProfile

class AddItemForm(forms.ModelForm):
    class Meta:
        fields = ('name', 'price', 'description', 'main_category', 'sec_category', 'owner')
        model = Item
