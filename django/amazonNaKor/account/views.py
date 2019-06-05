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
            # TODO (V2 - 귀국배송)
            # return HttpResponseRedirect('/account/registerPackage')
            return HttpResponseRedirect('/account/registerItem')
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
    recepient_form_data = request.session.get('recepient_form_data')
    if request.method == 'POST':
        item_formset = ItemInfoFormset(request.POST)

        if item_formset.is_valid() and request.POST.get("next"):
            item_index = 0
            item_set_data = []
            for item_form in item_formset.cleaned_data:
                if item_form['DELETE']:
                    continue
                request.session['recepient_form_data'] = request.session.get('recepient_form_data')
                # TODO (V2 - 귀국배송)
                # request.session['package_form_data'] = request.session.get('package_form_data')

                item_enum_key = str('item_%d_data' %item_index)
                item_index += 1
                item_set_data.append(item_form)

            request.session['total_items_count'] = item_index
            request.session['item_set_data'] = item_set_data

            return HttpResponseRedirect('/account/registerDelivery')
    else:
        item_formset = ItemInfoFormset()
    # TODO (V2 - 귀국배송)
    # package_form_data = request.session.get('package_form_data')
    # args = {'item_form': item_form, 'package_form_data': package_form_data, 'recepient_form_data': recepient_form_data}
    args = {'item_formset': item_formset, 'recepient_form_data': recepient_form_data}
    return render(request, 'account/reg_item_form.html', args)

@login_required
def registerDelivery(request):
    if request.method == 'POST':
        delivery_form = EnterDeliveryInfoForm(request.POST)
        recepient_form = EnterRecepientInfoForm(request.session.get('recepient_form_data'))

        # TODO (V2 - 귀국배송)
        # package_form = EnterPackageInfoForm(request.session.get('package_form_data'))

        if delivery_form.is_valid():
            recepient_obj = recepient_form.save(request.user)
            pkg_default_obj = Package.create(request.user, recepient_obj.id) # V1 - save the default values for the pkg (change for V2)

            delivery_obj = delivery_form.save(user=request.user, recepient=recepient_obj.id, package=pkg_default_obj.id)
            item_objs = []
            for item_form_data in request.session.get('item_set_data'):
                item_form = EnterItemInfoForm(item_form_data)
                item_obj = item_form.save(user=request.user, recepient=recepient_obj.id, package=pkg_default_obj.id, delivery=delivery_obj)
                item_objs.append(item_obj)

            # msg = EmailMessage(
            #            'Your order has been placed',
            #            '<strong>Order number:</strong> ' + str(delivery_obj.id) + \
            #            '<br><strong>Estimated Price:</strong> $' + str(delivery_obj.estimate) + \
            #            '<br><br>저희 서비스를 이용해주셔서 감사합니다. 배송을 원하시는 날자에 아래의 주소지로 물품을 가져와 주세요: <br><strong>1914 Junction ave. San Jose CA 95131</strong>' + \
            #            '<br><br>Click <a href="https://www.google.com/maps/place/Hangil+Trade+Inc/@37.3819114,-121.9119374,17z/data=!4m13!1m7!3m6!1s0x808fcbfa7ed17c2d:0x7efbb18e5b000330!2s1914+Junction+Ave,+San+Jose,+CA+95131!3b1!8m2!3d37.3819114!4d-121.9097487!3m4!1s0x808fc99055555555:0xbef41751b43676fd!8m2!3d37.3819114!4d-121.9097487">here</a> to open Google Maps' + \
            #            '<br><br><iframe width=600 height=450 src=https://www.google.com/maps/embed/v1/place?key=AIzaSyAQdms_gsY7auSuWlsGar5lfZbo5APfMAU&q=Hangil+Trade+Inc,San Jose></iframe>' + \
            #            '<br><br>영업일은 국가 공휴일 제외 월-금 아침 9시부터 오후 5시까지 입니다 (점심시간: 12시-1시). 결제는 cash or check only 입니다.',
            #            'sf.rocket.master@gmail.com',
            #            [request.user.email],
            #       )
            # msg.content_subtype = "html"
            # msg.send()
            return render(request,"account/order_summary.html",{'item_objs': item_objs, 'recepient_obj': recepient_obj, 'delivery_obj':delivery_obj, 'pkg_default_obj': pkg_default_obj})
        else:
            recepient_form_data = request.session.get('recepient_form_data')
            # TODO (V2 - 귀국배송)
            # package_form_data = request.session.get('package_form_data')
            item_form_data = request.session.get('item_form_data')

            # TODO (V2 - 귀국배송)
            # args = {'delivery_form': delivery_form, 'item_form_data': item_form_data, 'package_form_data': package_form_data, 'recepient_form_data': recepient_form_data}
            args = {'delivery_form': delivery_form, 'item_form_data': item_form_data, 'recepient_form_data': recepient_form_data}
            print(delivery_form.errors)
            return render(request, 'account/reg_delivery_form.html', args)
            
    else:
        total_items_count = request.session.get('total_items_count')
        delivery_form = EnterDeliveryInfoForm()
        recepient_form_data = request.session.get('recepient_form_data')
        # TODO (V2 - 귀국배송)
        # package_form_data = request.session.get('package_form_data')
        item_set_data = request.session.get('item_set_data')

        # TODO (V2 - 귀국배송)
        # args = {'delivery_form': delivery_form, 'item_form_data': item_form_data, 'package_form_data': package_form_data, 'recepient_form_data': recepient_form_data}
        args = {'delivery_form': delivery_form, 'item_set_data': item_set_data, 'recepient_form_data': recepient_form_data, 'total_items_count': total_items_count}
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

        recepients_list = Recepient.objects.filter(sender_email=user)
        for recepient in recepients_list:
            packages_list = Package.objects.filter(sender_email=user, recepient_id=recepient.id)
            for package in packages_list:
                items_list = Item.objects.filter(sender_email=user, recepient_id=recepient.id, package_id=package.id)
                for item in items_list:
                    deliveries_list = Delivery.objects.filter(sender_email=user, recepient_id=recepient.id, package_id=package.id, item=item)
                    response_arr = []
                    for delivery in deliveries_list:
                        response_arr = [delivery.id, sender_name, sender_phone, sender_address, delivery.id, 
                                        recepient.name, '', recepient.phone, recepient.postal_code, recepient.address, '', recepient.customs_id, '', '',
                                        package.pkg_type, '', package.width, package.length, package.height, package.weight, package.metric, package.box_count, package.standard_order, '', '',
                                        item.item_name, '', item.price, item.qty, item.item_code, item.hs_code,
                                        user.email, delivery.estimate, delivery.customs_fee_payee, '', delivery.method, '', '', delivery.dropped_off, delivery.sent]
                        writer.writerow([str(x).encode('euc-kr').decode('euc-kr') for x in response_arr])

    return response




