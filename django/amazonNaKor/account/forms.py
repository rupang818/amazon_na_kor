from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import User, Recepient, Package, Item

from localflavor.us.forms import USStateSelect, USZipCodeField


class RegistrationForm(UserCreationForm):
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
            'city',
            'state',
            'zip_code',
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
            'city',
            'state',
            'zip_code',
        )


class EnterRecepientInfoForm(forms.ModelForm):

    class Meta:
        model = Recepient
        fields = (
            'name',
            'phone',
            'postal_code',
            'address',
            'customs_id',
        )
        unique_together = (("sender_email", "name"),)

    def save(self, user = None, commit=True):
        recepient = super(EnterRecepientInfoForm, self).save(commit=False)
        recepient.sender_email = user   #PK1
        recepient.name = self.cleaned_data['name']
        recepient.phone = self.cleaned_data['phone']
        recepient.postal_code = self.cleaned_data['postal_code']
        recepient.address = self.cleaned_data['address']
        recepient.customs_id = self.cleaned_data['customs_id']


        if commit:
            recepient.save()
        return recepient

class EnterPackageInfoForm(forms.ModelForm):
    metric = forms.IntegerField(widget=forms.HiddenInput(), initial='2') 
    pkg_type = forms.IntegerField(widget=forms.HiddenInput(), initial='1')
    standard_order = forms.IntegerField(widget=forms.HiddenInput(), initial='0')

    class Meta:
        model = Package
        fields = (
            'width',
            'length',
            'height',
            'weight',
            'box_count',
        )
        unique_together = (("sender_email", "recepient_id"),)

    def save(self, user = None, recepient = None, commit=True):
        package = super(EnterPackageInfoForm, self).save(commit=False)
        package.sender_email = user   #PK1 (PK2 is 'id')
        package.recepient_id = recepient #PK3
        package.width = self.cleaned_data['width']
        package.length = self.cleaned_data['length']
        package.height = self.cleaned_data['height']
        package.weight = self.cleaned_data['weight']
        package.metric = self.cleaned_data['metric']
        package.box_count = self.cleaned_data['box_count']
        package.pkg_type = self.cleaned_data['pkg_type']
        package.standard_order = self.cleaned_data['standard_order']

        if commit:
            package.save()
        return package

class EnterItemInfoForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = (
            'item_name',
            'price',
            'qty',
        )
        unique_together = (("sender_email", "recepient_id", "package_id"),)

    def save(self, user = None, recepient = None, package = None, commit=True):
        item = super(EnterItemInfoForm, self).save(commit=False)
        item.sender_email = user   #PK1 (PK2 is 'id')
        item.recepient_id = recepient #PK3
        item.package_id = package #PK3
        item.item_name = self.cleaned_data['item_name']
        item.price = self.cleaned_data['price']
        item.qty = self.cleaned_data['qty']

        if commit:
            item.save()
        return item
