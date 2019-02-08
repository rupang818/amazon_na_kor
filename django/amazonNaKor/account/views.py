import csv
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.contrib.auth import update_session_auth_hash, authenticate, login
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.sessions.models import Session
from django.core.mail import EmailMessage

from .forms import *
from .models import *

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

            msg = EmailMessage(
                       'Your order has been placed',
                       '<strong>Order number:</strong> ' + str(delivery_obj.id) + '<br><strong>Estimated Price:</strong> $' + str(delivery_obj.estimate) + '<br><br>물품을 아래 주소지로 드랍해주세요: <br>1914 Junction ave. San Jose CA 95131',
                       'sf.rocket.master@gmail.com',
                       [request.user.email],
                  )
            msg.content_subtype = "html"
            msg.send()

            return render(request,"account/order_summary.html",{'delivery_obj':delivery_obj})
        else:
            recepient_form_data = request.session.get('recepient_form_data')
            package_form_data = request.session.get('package_form_data')
            item_form_data = request.session.get('item_form_data')

            args = {'delivery_form': delivery_form, 'item_form_data': item_form_data, 'package_form_data': package_form_data, 'recepient_form_data': recepient_form_data}
            print(delivery_form.errors)
            return render(request, 'account/reg_delivery_form.html', args)
            
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


@permission_required('admin.can_add_log_entry')
def download_csv(request):
    users = User.objects.all()

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="orders.csv"'

    writer = csv.writer(response, delimiter=',')
    writer.writerow(['번호', '보내는 사람 이름', '보내는 사람 전화', '보내는 사람 주소', '관리번호',
                     '받는사람 이름', '받는사람 전화', '받는사람 휴대폰', '받는사람 우편번호', '받는사람 주소', '받는사람 상세주소', '통관고유번호', '배송메모', '구분',
                     '수업유형', '판매 site URL', '가로(Cm)', '세로(Cm)', '높이(Cm)', '중량', '중량단위(1:Kg, 2:Lbs)', 'Box수량', '일반신청', '통관지정번호', '체결번호',
                     '상품명', '브랜드', '단가(USD)', '수량', '상품코드', 'HS코드',
                     'Email', 'Payable$', 'Custom', 'Type', 'Receive', 'Remark', 'PMT STTS', 'Dropped Off?', 'Fulfilled?'])

    for user in users:
        # User information
        sender_name = user.first_name + ' '+ user.last_name
        sender_phone = user.phone
        sender_address = ", ".join([" ".join([user.address1, user.address2]), user.city, user.state, user.zip_code])

        recepients_list = Recepient.objects.filter(sender_email=user)
        for recepient in recepients_list:
            packages_list = Package.objects.filter(sender_email=user, recepient_id=recepient.id)
            for package in packages_list:
                items_list = Item.objects.filter(sender_email=user, recepient_id=recepient.id, package_id=package.id)
                for item in items_list:
                    deliveries_list = Delivery.objects.filter(sender_email=user, recepient_id=recepient.id, package_id=package.id, item_id=item.id)
                    for delivery in deliveries_list:
                        writer.writerow([delivery.id, sender_name, sender_phone, sender_address, delivery.id, 
                                        recepient.name, '', recepient.phone, recepient.postal_code, recepient.address, '', recepient.customs_id, '', '',
                                        package.pkg_type, '', package.width, package.length, package.height, package.weight, package.metric, package.box_count, package.standard_order, '', '',
                                        item.item_name, '', item.price, item.qty, '', '',
                                        user.email, delivery.estimate, delivery.customs_fee_payee, '', delivery.method, '', '', delivery.dropped_off, delivery.sent])

    return response




