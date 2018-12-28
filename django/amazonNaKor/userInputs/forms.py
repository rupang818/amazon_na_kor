from django import forms

class InvoiceForm(forms.Form):
    # Sender info (EN)
    sender_name = forms.CharField(label='발신자 이름', max_length=100)
    sender_address = forms.CharField(label='발신자 주소', max_length=100)
    sender_phone = forms.CharField(label='발신자 전화번호', max_length=16)

    # Receiver info (KR)
    # receiver_name = forms.CharField(label='수령자 이름 (한글)', max_length=100)
    # receiver_phone = forms.CharField(label='수령자 전화번호', max_length=16)
    # receiver_postal_code = forms.IntegerField(label='수령자 우편번호')
    # receiver_address = forms.CharField(label='수령자 주소')
    # receiver_detail_address = forms.CharField(label='수령자 상세 주소', required=False)
    # customs_id = forms.CharField(label='통관고유번호', max_length=10)
    # transit_memo = forms.CharField(label='배송 메모', max_length=100, required=False)

    # # Package info
    # item_url = forms.CharField(label='판매 site URL', required=False)
    # width = forms.DecimalField(label='가로(cm)', min_value=0)
    # length = forms.DecimalField(label='세로(cm)', min_value=0)
    # height = forms.DecimalField(label='높이(cm)', min_value=0)
    # weight = forms.DecimalField(label='중량', min_value=0)
    # WEIGHT_METRIC_CHOICES =[('1','Kg'), ('2','lb')] # (value, label)
    # weight_metric = forms.ChoiceField(label='중량단위', choices=WEIGHT_METRIC_CHOICES, widget=forms.RadioSelect, required=False)
    # box_qty = forms.IntegerField(label='Box 수량', min_value=1)

    # # Item info (EN)
    # item_name = forms.CharField(label='상품명', max_length=100)
    # item_price = forms.DecimalField(label='가격(USD)', max_digits=6)
    # item_qty = forms.IntegerField(label='수량', min_value=1)

    # # Invoice info
    # email = forms.CharField(label='이메일', max_length=100)
    # final_price = forms.DecimalField(label='총 가격(USD)', max_digits=6)
