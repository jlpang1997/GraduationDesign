from django.http import HttpResponse

from django.shortcuts import render

from . import My_Spiders
shuimu=My_Spiders.Spider_shuimu('')

def hello(request):
    
    context          = {}
    context['hello'] = 'Hello World!'
    return render(request, 'hello.html', context)