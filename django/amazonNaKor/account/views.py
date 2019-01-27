from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.contrib.auth import update_session_auth_hash, authenticate, login
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.decorators import login_required
from django.contrib.sessions.models import Session

from .forms import RegistrationForm, EditProfileForm, EnterRecepientInfoForm, EnterPackageInfoForm, EnterItemInfoForm
from .models import User, Recepient, Package, Item

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
        recepient_form = EnterRecepientInfoForm(request.session.get('recepient_form_data'))
        package_form = EnterPackageInfoForm(request.session.get('package_form_data'))

        if item_form.is_valid():
            recepient_obj = recepient_form.save(request.user)
            package_obj = package_form.save(user=request.user, recepient=recepient_obj.id) #save 
            item_form.save(user=request.user, recepient=recepient_obj.id, package=package_obj.id)

            items_list=Item.objects.filter(sender_email=request.user)
            return render(request,"account/items.html",{'items_list':items_list})
            # TODO: show confirmation page
    else:
        item_form = EnterItemInfoForm()
        recepient_form_data = request.session.get('recepient_form_data')
        package_form_data = request.session.get('package_form_data')

        args = {'item_form': item_form, 'package_form_data': package_form_data, 'recepient_form_data': recepient_form_data}
        return render(request, 'account/reg_item_form.html', args)

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
    items_list=Item.objects.filter(sender_email=user)
    return render(request,"account/items.html",{'items_list':items_list})

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