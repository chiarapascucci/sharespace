from django import forms
from django.forms.widgets import EmailInput, HiddenInput, SelectMultiple 
from sharespace.models import Image, Item, Loan, User, UserProfile, Category, Sub_Category

class UserForm(forms.ModelForm):
    password = forms.CharField(widget = forms.PasswordInput())
    email = forms.EmailField(widget = forms.EmailInput())

    class Meta:
        fields = ('email', 'password', 'username', 'first_name', 'last_name')
        model = User

class UserProfileForm(forms.ModelForm):
    class Meta:
        fields = ('bio', 'picture', 'user_post_code')
        model = UserProfile

class ImageForm(forms.ModelForm):
    class Meta:
        model = Image
        fields = ('image',)

class AddItemForm(forms.ModelForm):
    class Meta:
        fields = ('name', 'description', 'main_category', 'sec_category', 'max_loan_len')
        model = Item

    def __init__(self, *args, **kwargs):
        super().__init__(*args, *kwargs)
        self.fields['sec_category'].queryset = Sub_Category.objects.none()

        if 'main_category' in self.data:
            try:
                main_cat_id = int(self.data.get('main_category'))
                print(main_cat_id)
                self.fields['sec_category'].queryset = Sub_Category.objects.filter(parent_id = main_cat_id)
            except (ValueError, TypeError):
                pass
        elif self.instance.pk:
            self.fields['sec_category'].queryset = Sub_Category.objects.all()


class AddItemFormWithAddress(AddItemForm):
    adr_line_1 = forms.CharField()
    adr_line_2 = forms.CharField()
    adr_line_3 = forms.CharField()
    adr_line_4 = forms.CharField()
    locality = forms.CharField()
    city = forms.CharField()
    county = forms.CharField()
    postcode = forms.CharField()

    class Meta(AddItemForm.Meta):
        fields = AddItemForm.Meta.fields + ('adr_line_1', 'adr_line_2', 'adr_line_3', 'adr_line_4',
                                            'locality', 'city', 'county')


class BorrowItemForm(forms.ModelForm):
    len_of_loan = forms.ChoiceField(choices=[], widget=forms.RadioSelect)
    class Meta:
        fields = ('len_of_loan',)
        model = Loan

