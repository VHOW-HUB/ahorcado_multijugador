from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Sala

def index(request):
    """Vista principal - menú de inicio"""
    return render(request, 'game/index.html')

def crear_sala(request):
    """Crear una nueva sala de juego"""
    codigo = Sala.generar_codigo()
    sala = Sala.objects.create(codigo=codigo)
    return redirect('game:sala', codigo_sala=codigo)

def unirse_sala(request, codigo_sala):
    """Unirse a una sala existente"""
    try:
        sala = Sala.objects.get(codigo=codigo_sala.upper())
        return redirect('game:sala', codigo_sala=sala.codigo)
    except Sala.DoesNotExist:
        return render(request, 'game/sala_no_existe.html', {'codigo': codigo_sala})

def sala(request, codigo_sala):
    """Vista de la sala de juego"""
    try:
        sala = Sala.objects.get(codigo=codigo_sala)
        return render(request, 'game/sala.html', {'codigo_sala': codigo_sala})
    except Sala.DoesNotExist:
        return redirect('game:index')
