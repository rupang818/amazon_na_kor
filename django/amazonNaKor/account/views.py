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
            reg_form_data = request.session.get('reg_form_data')

            args = {'form': form,'reg_form_data': reg_form_data}
            return render(request, 'account/reg_form.html', args)

    else:
        form = RegistrationForm()
        args = {'form': form}
        return render(request, 'account/reg_form.html', args)

@login_required
def registerRecipient(request):
    if request.method == 'POST':
        recipient_form = EnterRecipientInfoForm(request.POST)
        # TODO (V2 - 주소록): check for any existing recipients
        #Recipient.objects.filter(sender_email=user, ...)

        if recipient_form.is_valid():
            request.session['recipient_form_data'] = recipient_form.cleaned_data
            
            return HttpResponseRedirect('/account/registerItem')
    else:
        recipient_form = EnterRecipientInfoForm()
    args = {'recipient_form': recipient_form}
    return render(request, 'account/reg_recipient_form.html', args)

@login_required
def registerPackage(request):
    if request.method == 'POST':
        package_form = EnterPackageInfoForm(request.POST)

        if package_form.is_valid():
            request.session['recipient_form_data'] = request.session.get('recipient_form_data')
            request.session['item_set_data'] = request.session.get('item_set_data')
            request.session['package_form_data'] = package_form.cleaned_data
            
            return HttpResponseRedirect('/account/registerDelivery')

    else:
        package_form = EnterPackageInfoForm()
        recipient_form_data = request.session.get('recipient_form_data')
        item_set_data = request.session.get('item_set_data')

        args = {'item_set_data': item_set_data, 'package_form': package_form, 'recipient_form_data': recipient_form_data}
        return render(request, 'account/reg_package_form.html', args)

@login_required
def registerItem(request):
    recipient_form_data = request.session.get('recipient_form_data')
    if request.method == 'POST':
        item_formset = ItemInfoFormset(request.POST)

        if item_formset.is_valid() and request.POST.get("next"):
            item_index = 0
            item_set_data = []
            for item_form in item_formset.cleaned_data:
                if item_form['DELETE']:
                    continue
                request.session['recipient_form_data'] = request.session.get('recipient_form_data')

                item_enum_key = str('item_%d_data' %item_index)
                item_index += 1
                item_set_data.append(item_form)

            request.session['total_items_count'] = item_index
            request.session['item_set_data'] = item_set_data

            return HttpResponseRedirect('/account/registerPackage')
    else:
        item_formset = ItemInfoFormset()
    args = {'item_formset': item_formset, 'recipient_form_data': recipient_form_data}
    return render(request, 'account/reg_item_form.html', args)

@login_required
def registerDelivery(request):
    if request.method == 'POST':
        delivery_form = EnterDeliveryInfoForm(request.POST)
        recipient_form = EnterRecipientInfoForm(request.session.get('recipient_form_data'))
        package_form = EnterPackageInfoForm(request.session.get('package_form_data'))

        if delivery_form.is_valid():
            recipient_obj = recipient_form.save(request.user)
            pkg_obj = package_form.save(user=request.user, recipient=recipient_obj.id)

            delivery_obj = delivery_form.save(user=request.user, recipient=recipient_obj.id, package=pkg_obj.id)
            item_objs = []
            for item_form_data in request.session.get('item_set_data'):
                item_form = EnterItemInfoForm(item_form_data)
                item_obj = item_form.save(user=request.user, recipient=recipient_obj.id, package=pkg_obj.id, delivery=delivery_obj)
                item_objs.append(item_obj)

            msg = EmailMessage(
                       'Your order has been placed',
                       '<strong>Order number:</strong> ' + str(delivery_obj.id) + \
                       '<br><strong>Estimated Price:</strong> $' + str(delivery_obj.estimate) + \
                       '<br><br>저희 서비스를 이용해주셔서 감사합니다. 배송을 원하시는 날자에 아래의 주소지로 물품을 가져와 주세요: <br><strong>1914 Junction ave. San Jose CA 95131</strong> ' + \
                       '(Click <a href="https://www.google.com/maps/place/Hangil+Trade+Inc/@37.3819114,-121.9119374,17z/data=!4m13!1m7!3m6!1s0x808fcbfa7ed17c2d:0x7efbb18e5b000330!2s1914+Junction+Ave,+San+Jose,+CA+95131!3b1!8m2!3d37.3819114!4d-121.9097487!3m4!1s0x808fc99055555555:0xbef41751b43676fd!8m2!3d37.3819114!4d-121.9097487">here</a> to open Google Maps)' + \
                       '<br><br>배송 추적은 아래 링크에서 확인하신 수 있으며 패키지 드랍 다음날 위 오더넘버로 조회 가능합니다 ' + \
                       '(Click <a href="https://docs.google.com/spreadsheets/d/1HDzzWQpX9ReACKX6i9DUOVQUBGjRCm9MKhTvoAcK7UM/edit#gid=0" target="_blank">here</a> to open Tracking information)' + \
                       # '<br><br><iframe width=600 height=450 src=https://www.google.com/maps/embed/v1/place?key=AIzaSyAQdms_gsY7auSuWlsGar5lfZbo5APfMAU&q=Hangil+Trade+Inc,San Jose></iframe>' + \
                       '<br><br>영업일은 국가 공휴일 제외 월-금 아침 9시부터 오후 5시까지 입니다 (점심시간: 12시-1시). <br>결제는 cash or check only 입니다.',
                       'info@sfrocket.com',
                       [request.user.email],
                  )
            msg.content_subtype = "html"
            msg.send()
            
            return render(request,"account/order_summary.html",{'item_objs': item_objs, 'recipient_obj': recipient_obj, 'delivery_obj':delivery_obj, 'pkg_obj': pkg_obj})
        else:
            recipient_form_data = request.session.get('recipient_form_data')
            package_form_data = request.session.get('package_form_data')
            item_set_data = request.session.get('item_set_data')

            args = {'delivery_form': delivery_form, 'item_set_data': item_set_data, 'package_form_data': package_form_data, 'recipient_form_data': recipient_form_data}
            return render(request, 'account/reg_delivery_form.html', args)
            
    else:
        total_items_count = request.session.get('total_items_count')
        delivery_form = EnterDeliveryInfoForm()
        recipient_form_data = request.session.get('recipient_form_data')
        package_form_data = request.session.get('package_form_data')
        item_set_data = request.session.get('item_set_data')

        args = {'delivery_form': delivery_form, 'item_set_data': item_set_data, 'package_form_data': package_form_data, 'recipient_form_data': recipient_form_data}
        return render(request, 'account/reg_delivery_form.html', args)

@login_required
def view_profile(request):
    args = {'user': request.user}
    return render(request, 'account/profile.html', args)

@login_required
def view_recipients(request):
    user=request.user
    recipients_list=Recipient.objects.filter(sender_email=user)
    return render(request,"account/recipients.html",{'recipients_list':recipients_list})

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

def findus(request):
    return render(request, 'account/findus.html')

@permission_required('admin.can_add_log_entry')
def download_csv(request):
    users = User.objects.all()

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="orders.csv"'

    writer = csv.writer(response, delimiter=',')
    raw_arr = ['번호', '보내는 사람 이름', '보내는 사람 전화', '보내는 사람 주소', '관리번호',
                 '받는사람 이름', '받는사람 전화', '받는사람 휴대폰', '받는사람 우편번호', '받는사람 주소', '받는사람 상세주소', '통관고유번호', '배송메모', '구분',
                 '수업유형', '판매 site URL', '가로(Cm)', '세로(Cm)', '높이(Cm)', '중량', '중량단위(1:Kg, 2:Lbs)', 'Box수량', '일반신청', '통관지정번호', '체결번호',
                 '상품명', '브랜드', '단가(USD)', '수량', '상품코드', 'HS코드',
                 'Email', 'Payable($)', 'Custom', 'Type', 'Receive', 'Remark', 'PMT STTS', 'Dropped Off?', 'Fulfilled?']
    writer.writerow([x.encode('euc-kr').decode('euc-kr') for x in raw_arr])


    for user in users:
        # User information
        sender_name = user.first_name + ' '+ user.last_name
        sender_phone = user.phone
        sender_address = ", ".join([" ".join([user.address1, user.address2]), user.city, user.state, user.zip_code])

        recipients_list = Recipient.objects.filter(sender_email=user)
        for recipient in recipients_list:
            packages_list = Package.objects.filter(sender_email=user, recipient_id=recipient.id)
            for package in packages_list:
                items_list = Item.objects.filter(sender_email=user, recipient_id=recipient.id, package_id=package.id)
                for item_index in range(len(items_list)):
                    item = items_list[item_index]
                    deliveries_list = Delivery.objects.filter(sender_email=user, recipient_id=recipient.id, package_id=package.id, item=item)
                    response_arr = []
                    for delivery in deliveries_list:
                        if delivery.dropped_off and not delivery.sent:
                            if item_index == 0:
                                response_arr = [delivery.id, sender_name, sender_phone, sender_address, delivery.id, 
                                                recipient.name, '', recipient.phone, recipient.postal_code, recipient.address, '', recipient.customs_id, '', '',
                                                package.pkg_type, '', package.width, package.length, package.height, package.weight, package.metric, package.box_count, package.standard_order, '', '',
                                                item.item_name, '', item.price, item.qty, item.item_code, item.hs_code,
                                                user.email, delivery.estimate, delivery.customs_fee_payee, '', delivery.method, '', '', delivery.dropped_off, delivery.sent]
                            else:
                                prepending_empty_arr = ['' for i in range(25)]
                                postpending_empty_arr = ['' for i in range(9)]
                                response_arr = prepending_empty_arr + [item.item_name, '', item.price, item.qty, item.item_code, item.hs_code] + postpending_empty_arr
                            writer.writerow([str(x).encode('euc-kr').decode('euc-kr') for x in response_arr])

    return response




