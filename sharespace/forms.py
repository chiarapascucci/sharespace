from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.forms.widgets import EmailInput, HiddenInput, SelectMultiple, SelectDateWidget
from registration.forms import RegistrationForm
from sharespace.models import Image, Item, Loan, CustomUser, UserProfile, Category, Sub_Category, \
    UserToAdminReportNotAboutUser, PurchaseProposal
from sharespace.utils import get_booking_calendar_for_item_for_month


class UserForm(UserCreationForm):
   # required_css_class = 'required'
    print("using my custom reg form")
    # password = forms.CharField(widget = forms.PasswordInput())
    email = forms.EmailField(widget = forms.EmailInput())
    username = forms.CharField(max_length=55)

    def clean_email(self):
        data = self.cleaned_data['email']
        return data.lower()

    class Meta:
        fields = ('email', 'username',)
        model = CustomUser

class UserProfileForm(forms.ModelForm):
    class Meta:
        fields = ('bio', 'picture', 'user_post_code')
        model = UserProfile

class EditUserProfileBasicForm(forms.ModelForm):
    picture = forms.ImageField(required=False)
    bio = forms.CharField(required=False)
    class Meta:
        model = UserProfile
        fields = ('bio', 'picture', )

class ImageForm(forms.ModelForm):
    class Meta:
        model = Image
        fields = ('image',)

class EditItemForm(forms.ModelForm):
    class Meta:
        fields = ('name', 'description', 'main_category', 'sec_category', 'max_loan_len')
        model = Item

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





class SubmitReportForm(forms.ModelForm):

    class Meta:
        model = UserToAdminReportNotAboutUser
        fields = ('report_title', 'report_body', 'report_sender', 'report_date_out')
        widgets = {'report_sender': forms.HiddenInput(),
                   'report_receiver': forms.HiddenInput(),
                   'report_date_out' : forms.HiddenInput(),
                    }


class SubmitPurchaseProposalForm(forms.ModelForm):

    class Meta:
        model = PurchaseProposal
        fields = ('proposal_item_name', 'proposal_cat', 'proposal_sub_cat',
                  'proposal_item_description', 'proposal_price', 'proposal_contact',)
