from django.urls import path 
from sharespace import views 

app_name = 'sharespace'

urlpatterns = [path('', views.index, name='index'),
]