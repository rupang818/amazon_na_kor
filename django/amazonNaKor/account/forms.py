from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import User#, UserProfile

class RegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    phone = forms.IntegerField(min_value=1, widget=forms.NumberInput(attrs={'size':'11'}))
    address1 = forms.CharField(max_length=1024)
    address2 = forms.CharField(max_length=1024)
    zip_code = forms.CharField(max_length=12)
    city = forms.CharField(max_length=1024)
    state = forms.CharField(max_length=1024)

    class Meta:
        model = User
        fields = (
            'first_name', 
            'last_name',
            'email',
            'password1',
            'password2',
            'phone',
            'address1',
            'address2',
            'zip_code',
            'city',
            'state'
        )

    def save(self, commit=True):
        user = super(RegistrationForm, self).save(commit=False) # commit=false => I haven't finished editing yet
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']
        user.phone = self.cleaned_data['phone']
        user.address1 = self.cleaned_data['address1']        
        user.address2 = self.cleaned_data['address2']
        user.zip_code = self.cleaned_data['zip_code']
        user.city = self.cleaned_data['city']
        user.state = self.cleaned_data['state']

        if commit:
            user.save()

        return user

class EditProfileForm(UserChangeForm):
    address2 = forms.CharField(max_length=1024)
    
    class Meta:
        model = User
        fields = (
            'email',
            'first_name',
            'last_name',
            'password',
            'phone',
            'address1',
            'address2',
            'zip_code',
            'city',
            'state'
        )
        # exclude = ()




