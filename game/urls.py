from django.urls import path
from . import views

app_name = 'game'

urlpatterns = [
    path('', views.index, name='index'),
    path('crear-sala/', views.crear_sala, name='crear_sala'),
    path('unirse/<str:codigo_sala>/', views.unirse_sala, name='unirse_sala'),
    path('sala/<str:codigo_sala>/', views.sala, name='sala'),
]
