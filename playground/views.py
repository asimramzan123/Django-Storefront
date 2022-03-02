from django.http import HttpResponse
from django.shortcuts import render
from django.http import HttpResponse
# Create your views here.

def hello(request):
    # return HttpResponse('Welcome in DJango')
    return render(request, 'hello.html',{'name':'Asim'})
