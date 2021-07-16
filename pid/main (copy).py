from django.shortcuts import render
from rest_framework.decorators import api_view
from od_predict import *


# Create your views here.
@api_view(('POST',))
def hello(request):
    
    return render(od_predict.combine())
