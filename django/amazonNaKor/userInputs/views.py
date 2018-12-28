from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render

from .forms import InvoiceForm


def get(self, request):
    form = InvoiceForm()
    return render(request, self.template_name, {'form': form, 'invoice_id': 2})

def post(self, request):
    form = InvoiceForm(request.POST) # TODO: input number of existing orders
    if form.is_valid():
        form.save()
        text = form.cleaned_data['post']
        form = InvoiceForm()
        return HttpResponseRedirect('/thanks/')
    args = {'form': form, 'text': text}
    return render(request, self.template_name, args)

def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")

def thanks(request):
    return HttpResponse("Thanks for the submission! You will shortly get an e-mail")

def get_invoice(request):
    template_name = 'userInputs/invoice.html'

    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = InvoiceForm(request.POST) # TODO: input number of existing orders
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:
            return HttpResponseRedirect('/thanks/')

    # if a GET (or any other method) we'll create a blank form
    else:
        form = InvoiceForm() 

    return render(request, template_name, {'form': form, 'invoice_id': 4}) # TODO: input number of existing orders