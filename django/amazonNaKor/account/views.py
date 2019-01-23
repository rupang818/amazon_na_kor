from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.decorators import login_required

from .forms import RegistrationForm, EditProfileForm, EnterRecepientInfoForm, EnterPackageInfoForm
from .models import User, Recepient, Package

def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)

        if form.is_valid():
            form.save()
            # TODO: make sure to auto-login after registering
            # #get the username and password
            # email = self.request.POST['email']
            # password = self.request.POST['password1']
            # #authenticate user then login
            # email = authenticate(username=username, password=password)
            # login(self.request, user)
            return HttpResponseRedirect('/account/')
    else:
        form = RegistrationForm()
        args = {'form': form}
        return render(request, 'account/reg_form.html', args)

@login_required
def registerRecepient(request):
    if request.method == 'POST':
        form = EnterRecepientInfoForm(request.POST)

        if form.is_valid():
            form.save(request.user)
            return HttpResponseRedirect('/account/registerPackage')
    else:
        form = EnterRecepientInfoForm()
        args = {'form': form}
        return render(request, 'account/reg_recepient_form.html', args)

@login_required
def registerPackage(request):
    if request.method == 'POST':
        form = EnterPackageInfoForm(request.POST)

        if form.is_valid():
            form.save(request.user)
            # return HttpResponseRedirect('/account/registerPackage')
            packages_list=Package.objects.filter(sender_email=request.user)
            return render(request,"account/packages.html",{'packages_list':packages_list})

    else:
        # TODO: show the related Recepient info using (email, receiver_name) as PK
        form = EnterPackageInfoForm()
        args = {'form': form}
        return render(request, 'account/reg_package_form.html', args)

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