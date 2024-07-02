from django.contrib.auth.models import User
# UserCreation form contains 3 rows -> Username, Password, Conf.password
from django.contrib.auth.forms import UserCreationForm
from libapp.models import Book,UserImage,UserPaymentDetails
from django import forms

# creating form fields based on auth_user table
# class UserForm is user-defined
# UserCreation form contains 3 rows -> Username, Password, Conf.password
class UserForm(UserCreationForm):
    class Meta:
        # using auth_user model to create form fields
        model = User
        # auth_user model fields used as form fields
        fields = ['first_name','last_name','username','email']

class UserProfileUpdateForm(forms.Form):
        first_name = forms.CharField(max_length=70)
        last_name = forms.CharField(max_length=70)
        username = forms.CharField(max_length=70)
        email = forms.CharField(max_length=70)

# creating custom form using 'Form' class
class BookForm(forms.Form):
        title = forms.CharField(max_length=50)
        author = forms.CharField(max_length=50)
        small_description = forms.CharField(max_length=1000)
        price = forms.CharField(max_length=5)

# payment method form
class PaymentOptionsForm(forms.Form):
    payment_methods = forms.ChoiceField(choices=(('1','Debit Card'),('2','NetBanking'),('3','Upi')))

class DebitCardForm(forms.ModelForm):
    class Meta:
        model = UserPaymentDetails
        fields = ['name','debit_card_num','cvv','price']

class NetBankingRegisterForm(forms.Form):
    first_name = forms.CharField(max_length=50)
    last_name = forms.CharField(max_length=50)
    account_number = forms.CharField(max_length=15)
    mobile_number = forms.CharField(max_length=10)
    username = forms.CharField(max_length=50)
    password = forms.CharField(max_length=30,widget=forms.PasswordInput)
 
class NetBankingLoginForm(forms.Form):
    username = forms.CharField(max_length=50)
    password = forms.CharField(max_length=30,widget=forms.PasswordInput)

class NetBankingTransactionDetails(forms.Form):
    amount = forms.CharField(max_length=50)

class UpiTransactionDetails(forms.Form):
    amount = forms.CharField(max_length=50)

class ImageForm(forms.ModelForm):
    class Meta:
        model = UserImage
        fields = ['image']