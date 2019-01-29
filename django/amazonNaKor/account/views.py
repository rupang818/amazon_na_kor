from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.contrib.auth import update_session_auth_hash, authenticate, login
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.decorators import login_required
from django.contrib.sessions.models import Session
from django.core.mail import send_mail

from .forms import RegistrationForm, EditProfileForm, EnterRecepientInfoForm, EnterPackageInfoForm, EnterItemInfoForm, EnterDeliveryInfoForm
from .models import User, Recepient, Package, Item, Delivery

def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)

        if form.is_valid():
            form.save()

            # Log-in automatically once registered
            email = request.POST['email']
            password = request.POST['password1']
            user = authenticate(username=email, password=password)
            login(request, user)
            return HttpResponseRedirect('/account/')

    else:
        form = RegistrationForm()
        args = {'form': form}
        return render(request, 'account/reg_form.html', args)

@login_required
def registerRecepient(request):
    if request.method == 'POST':
        recepient_form = EnterRecepientInfoForm(request.POST)
        # TODO (V2 - 주소록): check for any existing recepients
        #Recepient.objects.filter(sender_email=user, ...)

        if recepient_form.is_valid():
            request.session['recepient_form_data'] = recepient_form.cleaned_data
            return HttpResponseRedirect('/account/registerPackage')
    else:
        recepient_form = EnterRecepientInfoForm()
        args = {'recepient_form': recepient_form}
        return render(request, 'account/reg_recepient_form.html', args)

@login_required
def registerPackage(request):
    if request.method == 'POST':
        package_form = EnterPackageInfoForm(request.POST)

        if package_form.is_valid():
            request.session['recepient_form_data'] = request.session.get('recepient_form_data')
            request.session['package_form_data'] = package_form.cleaned_data
            return HttpResponseRedirect('/account/registerItem')

    else:
        package_form = EnterPackageInfoForm()
        recepient_form_data = request.session.get('recepient_form_data')

        args = {'package_form': package_form, 'recepient_form_data': recepient_form_data}
        return render(request, 'account/reg_package_form.html', args)

@login_required
def registerItem(request):
    if request.method == 'POST':
        item_form = EnterItemInfoForm(request.POST)

        if item_form.is_valid():
            request.session['recepient_form_data'] = request.session.get('recepient_form_data')
            request.session['package_form_data'] = request.session.get('package_form_data')
            request.session['item_form_data'] = item_form.cleaned_data
            return HttpResponseRedirect('/account/registerDelivery')
    else:
        item_form = EnterItemInfoForm()
        recepient_form_data = request.session.get('recepient_form_data')
        package_form_data = request.session.get('package_form_data')

        args = {'item_form': item_form, 'package_form_data': package_form_data, 'recepient_form_data': recepient_form_data}
        return render(request, 'account/reg_item_form.html', args)

@login_required
def registerDelivery(request):
    if request.method == 'POST':
        delivery_form = EnterDeliveryInfoForm(request.POST)
        item_form = EnterItemInfoForm(request.session.get('item_form_data'))
        recepient_form = EnterRecepientInfoForm(request.session.get('recepient_form_data'))
        package_form = EnterPackageInfoForm(request.session.get('package_form_data'))
        # TODO: don't proceed until the agreement_signed is true - also send reminder to user, if not clicked

        if delivery_form.is_valid():
            recepient_obj = recepient_form.save(request.user)
            package_obj = package_form.save(user=request.user, recepient=recepient_obj.id) #save 
            item_obj = item_form.save(user=request.user, recepient=recepient_obj.id, package=package_obj.id)
            delivery_obj = delivery_form.save(user=request.user, recepient=recepient_obj.id, package=package_obj.id, item=item_obj.id)

            send_mail('Your order has been placed - Order number: ' + str(delivery_obj.id),
                        '물품을 아래 주소지로 드랍해주세요: 1914 Junction ave. San Jose CA 95131',
                        'sf.rocket.master@gmail.com',
                        [request.user.email],
                        fail_silently=False)

            return render(request,"account/order_summary.html",{'delivery_obj':delivery_obj})
    else:
        delivery_form = EnterDeliveryInfoForm()
        recepient_form_data = request.session.get('recepient_form_data')
        package_form_data = request.session.get('package_form_data')
        item_form_data = request.session.get('item_form_data')

        args = {'delivery_form': delivery_form, 'item_form_data': item_form_data, 'package_form_data': package_form_data, 'recepient_form_data': recepient_form_data}
        return render(request, 'account/reg_delivery_form.html', args)

@login_required
def view_profile(request):
    args = {'user': request.user}
    return render(request, 'account/profile.html', args)

@login_required
def view_recepients(request):
    user=request.user
    recepients_list=Recepient.objects.filter(sender_email=user)
    return render(request,"account/recepients.html",{'recepients_list':recepients_list})

@login_required
def view_packages(request):
    user=request.user
    packages_list=Package.objects.filter(sender_email=user)
    return render(request,"account/packages.html",{'packages_list':packages_list})

@login_required
def view_items(request):
    user=request.user
    item_list=Item.objects.filter(sender_email=user)
    return render(request,"account/items.html",{'item_list':item_list})

@login_required
def view_items(request):
    user=request.user
    items_list=Item.objects.filter(sender_email=user)
    return render(request,"account/items.html",{'items_list':items_list})

@login_required
def view_order_summary(request):
    args = {'user': request.user}
    return render(request, 'account/order_summary.html', args)

@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = EditProfileForm(request.POST, instance=request.user)

        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/account/profile')
    else:
        form = EditProfileForm(instance=request.user)
        args = {'form': form}
        return render(request, 'account/edit_profile.html', args)
        
@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(data=request.POST, user=request.user)

        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)
            return HttpResponseRedirect('/account/profile')
        else:
            return HttpResponseRedirect('/account/change-password')
    else:
        form = PasswordChangeForm(user=request.user)
        args = {'form': form}
        return render(request, 'account/change_password.html', args)

# TODO: if registered, allow. Otherwise, direct to register.html
def home(request):
    return render(request, 'account/home.html')