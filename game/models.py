from django.db import models
import random
import string

class Sala(models.Model):
    codigo = models.CharField(max_length=6, unique=True, primary_key=True)
    creada_en = models.DateTimeField(auto_now_add=True)
    jugadores_conectados = models.IntegerField(default=0)
    
    def __str__(self):
        return f"Sala {self.codigo}"
    
    @classmethod
    def generar_codigo(cls):
        while True:
            codigo = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
            if not cls.objects.filter(codigo=codigo).exists():
                return codigo
