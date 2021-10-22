from django import forms
from django.forms.widgets import EmailInput, HiddenInput, SelectMultiple 
from sharespace.models import Image, Item, Loan, User, UserProfile

class UserForm(forms.ModelForm):
    password = forms.CharField(widget = forms.PasswordInput())
    email = forms.EmailField(widget = forms.EmailInput())

    class Meta:
        fields = ('email', 'password', 'username', 'first_name', 'last_name')
        model = User

class UserProfileForm(forms.ModelForm):
    class Meta:
        fields = ('bio', 'picture')
        model = UserProfile

class ImageForm(forms.ModelForm):
    class Meta:
        model = Image
        fields = ('image',)

class AddItemForm(forms.ModelForm):
    owner = forms.ModelMultipleChoiceField(queryset=UserProfile.objects.all())
    class Meta:
        fields = ('name', 'price', 'description', 'main_category', 'sec_category', 'owner', 'max_loan_len')
        model = Item

class BorrowItemForm(forms.ModelForm):
    class Meta:
        fields = ('len_of_loan',)
        model = Loan
