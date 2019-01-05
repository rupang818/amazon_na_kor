from django.http import HttpResponse, HttpResponseRedirect

def login_redirect(request):
    return HttpResponseRedirect('/account/login')