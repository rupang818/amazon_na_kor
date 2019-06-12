from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import User, Recepient, Package, Item, Delivery

from localflavor.us.forms import USStateSelect, USZipCodeField
from django.forms.formsets import formset_factory
from djangoformsetjs.utils import formset_media_js

def isEnglishOrKorean(input_s):
    k_count = 0
    e_count = 0
    for c in input_s:
        if ord('가') <= ord(c) <= ord('힣'):
            k_count+=1
        elif ord('a') <= ord(c.lower()) <= ord('z'):
            e_count+=1
    return "k" if k_count>1 else "e"

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
        widgets={
            'address': forms.TextInput(attrs={'size': 32})
        }

    def clean_name(self):
        name = self.cleaned_data['name']
        if isEnglishOrKorean(name) is "e":
            raise forms.ValidationError("받는사람 이름은 한글로만 작성 해주세요")
        return name

    def clean_address(self):
        address = self.cleaned_data['address']
        if isEnglishOrKorean(address) is "e":
            raise forms.ValidationError("받는사람 주소는 한글로만 작성 해주세요")
        return address

    def clean_phone(self):
        phone = self.cleaned_data['phone']
        try:
            phone_cleaned = int(phone.replace('-',''))
        except ValueError:
            raise forms.ValidationError("올바른 전화번호를 입력해주세요 (예: 010-1234-5678)")
        return phone

    def clean_postal_code(self):
        postal_code = self.cleaned_data['postal_code']
        try:
            postal_code_cleaned = int(postal_code.replace('-',''))
        except ValueError:
            raise forms.ValidationError("올바른 우편번호를 입력해주세요 (예: 100-011)")
        return postal_code


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

    # TODO (V2): remove these to let the user specify these
    length = forms.IntegerField(widget=forms.HiddenInput(), initial='10')
    width = forms.IntegerField(widget=forms.HiddenInput(), initial='10')
    height = forms.IntegerField(widget=forms.HiddenInput(), initial='10') 

    class Meta:
        model = Package
        fields = (
            # TODO (V2): uncomment these to let the user specify
            # 'width',
            # 'length',
            # 'height',
            'box_count',
            'weight',
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

    class Media(object):
        # The form must have `formset_media_js` in its Media
        js = formset_media_js + (
            # Other form javascript...
        )

    class Meta:
        model = Item
        fields = (
            'item_name',
            'price',
            'qty',
            'hs_code',
        )
        unique_together = (("sender_email", "recepient_id", "package_id"),)

    def clean_price(self):
        price = self.cleaned_data['price']
        if price <= 0:
            raise forms.ValidationError("단가는 0 이상으로 책정해주세요")
        return price

    def clean_item_name(self):
        item_name = self.cleaned_data['item_name']
        if isEnglishOrKorean(item_name) is "k":
            raise forms.ValidationError("상품명은 영문으로만 작성 해주세요")
        return item_name

    def save(self, user = None, recepient = None, package = None, delivery= None, commit = True):
        item = super(EnterItemInfoForm, self).save(commit=False)
        item.delivery = delivery
        item.sender_email = user   #PK1 (PK2 is 'id')
        item.recepient_id = recepient #PK3
        item.package_id = package #PK3
        item.item_name = self.cleaned_data['item_name']
        item.hs_code = self.cleaned_data['hs_code']
        item.item_code = dict(item.ITEM_CODES).get(item.hs_code)
        item.price = self.cleaned_data['price']
        item.qty = self.cleaned_data['qty']

        if commit:
            item.save()
        return item
ItemInfoFormset = formset_factory(EnterItemInfoForm, can_delete=True)

class EnterDeliveryInfoForm(forms.ModelForm):
    class Meta:
        model = Delivery
        fields = (
            'customs_fee_payee',
            'method',
            'agreement_signed',
        )
    def clean_agreement_signed(self):
        agreement_signed = self.cleaned_data['agreement_signed']
        if agreement_signed == False:
            raise forms.ValidationError("\"위 사항에 동의합니다\"를 클릭해주세요 (Agreement must be acknowledged)", code='invalid')
        return agreement_signed

    def calculate_estimate(self, weight, customs_fee_payee, method):
        estimate = 8.5 + weight * 1.5 
        if customs_fee_payee == 'SENDER':
            estimate += 5.0
        if method == 'UPS':
            estimate += 10.0
        return estimate

    def save(self, user = None, recepient = None, package = None, commit=True):
        delivery = super(EnterDeliveryInfoForm, self).save(commit=False)
        delivery.sender_email = user
        delivery.recepient_id = recepient
        delivery.package_id = package
        delivery.customs_fee_payee = self.cleaned_data['customs_fee_payee']
        delivery.method = self.cleaned_data['method']
        delivery.agreement_signed = self.cleaned_data['agreement_signed']
        delivery.dropped_off = False
        delivery.sent = False

        # Calculate the estimated cost
        _pkg_obj_list=Package.objects.filter(id=package)
        _weight=_pkg_obj_list[0].weight
        delivery.estimate = self.calculate_estimate(_weight, delivery.customs_fee_payee, delivery.method)

        if commit:
            delivery.save()
        return delivery


