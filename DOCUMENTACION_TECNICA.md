# 🔧 DOCUMENTACIÓN TÉCNICA

## Arquitectura del Sistema

### Stack Tecnológico

```
┌─────────────────────────────────────────┐
│           CLIENTE (Browser)              │
│  HTML + CSS + JavaScript + WebSocket    │
└───────────────┬─────────────────────────┘
                │
                │ WebSocket (ws://)
                │
┌───────────────▼─────────────────────────┐
│         SERVIDOR (Django)                │
│  ┌─────────────────────────────────┐   │
│  │  Django Channels (ASGI)         │   │
│  │  - WebSocket Consumer           │   │
│  │  - Estado en memoria            │   │
│  └─────────────────────────────────┘   │
│  ┌─────────────────────────────────┐   │
│  │  Django Views (HTTP)            │   │
│  │  - Creación de salas            │   │
│  │  - Renderizado de templates     │   │
│  └─────────────────────────────────┘   │
└───────────────┬─────────────────────────┘
                │
                │
┌───────────────▼─────────────────────────┐
│      BASE DE DATOS (SQLite)             │
│  - Tabla: Sala (código único)          │
└─────────────────────────────────────────┘
```

## Flujo de Conexión

### 1. Creación de Sala

```python
# views.py
def crear_sala(request):
    codigo = Sala.generar_codigo()  # Genera código aleatorio 6 chars
    sala = Sala.objects.create(codigo=codigo)
    return redirect('game:sala', codigo_sala=codigo)
```

### 2. Conexión WebSocket

```javascript
// Cliente
const socket = new WebSocket('ws://localhost:8000/ws/sala/ABC123/');

socket.onopen = () => {
    console.log('Conectado');
};
```

```python
# consumers.py
async def connect(self):
    self.codigo_sala = self.scope['url_route']['kwargs']['codigo_sala']
    self.room_group_name = f'sala_{self.codigo_sala}'
    
    # Unirse al grupo de la sala
    await self.channel_layer.group_add(
        self.room_group_name,
        self.channel_name
    )
    
    await self.accept()
```

## Estructura de Mensajes WebSocket

### Mensajes Cliente → Servidor

#### 1. Enviar Palabra Secreta
```json
{
    "tipo": "enviar_palabra",
    "palabra": "PYTHON"
}
```

#### 2. Adivinar Letra
```json
{
    "tipo": "adivinar_letra",
    "letra": "A"
}
```

#### 3. Reconexión
```json
{
    "tipo": "reconectado"
}
```

### Mensajes Servidor → Cliente

#### 1. Jugador Conectado
```json
{
    "tipo": "jugador_conectado",
    "jugador_id": "jugador1",
    "total_jugadores": 1,
    "tu_id": "jugador1"
}
```

#### 2. Iniciar Ronda
```json
{
    "tipo": "iniciar_ronda",
    "jugador_adivinando": "jugador2",
    "ronda": 1,
    "puntos": {"jugador1": 0, "jugador2": 0},
    "tu_id": "jugador1"
}
```

#### 3. Palabra Recibida
```json
{
    "tipo": "palabra_recibida",
    "longitud_palabra": 6,
    "tiempo_restante": 90
}
```

#### 4. Letra Correcta
```json
{
    "tipo": "letra_correcta",
    "letra": "A",
    "palabra_revelada": "A____A",
    "errores": 0
}
```

#### 5. Letra Incorrecta
```json
{
    "tipo": "letra_incorrecta",
    "letra": "Z",
    "palabra_revelada": "_____",
    "errores": 1
}
```

#### 6. Ronda Terminada
```json
{
    "tipo": "ronda_terminada",
    "ganador": "jugador1",
    "palabra_secreta": "PYTHON",
    "puntos": {"jugador1": 1, "jugador2": 0},
    "siguiente_adivinando": "jugador1",
    "ronda": 2
}
```

#### 7. Juego Terminado
```json
{
    "tipo": "juego_terminado",
    "ganador": "jugador1",
    "puntos": {"jugador1": 5, "jugador2": 3}
}
```

#### 8. Jugador Desconectado
```json
{
    "tipo": "jugador_desconectado",
    "jugador_id": "jugador2"
}
```

#### 9. Jugador Reconectado
```json
{
    "tipo": "jugador_reconectado",
    "jugador_id": "jugador2"
}
```

## Estado de la Sala (En Memoria)

```python
# consumers.py - Variable de clase
salas_estado = {
    'ABC123': {
        'jugadores': [
            {'id': 'jugador1', 'channel_name': 'channel_abc'},
            {'id': 'jugador2', 'channel_name': 'channel_xyz'}
        ],
        'juego_iniciado': True,
        'ronda_actual': 3,
        'jugador_adivinando': 'jugador1',
        'palabra_secreta': 'PYTHON',
        'letras_adivinadas': ['P', 'Y', 'O'],
        'errores': 2,
        'puntos': {'jugador1': 2, 'jugador2': 1},
        'tiempo_restante': 45,
        'timer_activo': True,
        'desconectado': None,
        'tiempo_espera_reconexion': 20
    }
}
```

## Lógica del Juego

### Secuencia Completa de una Ronda

```
1. INICIAR_RONDA
   ├─ Servidor asigna aleatoriamente quién adivina
   ├─ Resetea errores, letras adivinadas, timer
   └─ Notifica a ambos jugadores

2. JUGADOR_ESCRIBE
   ├─ Jugador que NO adivina ve input de texto
   ├─ Escribe palabra (mín. 3 letras)
   └─ Envía "enviar_palabra" al servidor

3. SERVIDOR_PROCESA_PALABRA
   ├─ Guarda palabra_secreta en estado
   ├─ Inicializa letras_adivinadas = []
   └─ Envía "palabra_recibida" con longitud

4. JUGADOR_ADIVINA
   ├─ Ve teclado virtual + guiones bajos
   ├─ Timer de 90 segundos comienza
   └─ Click en letra → "adivinar_letra"

5. SERVIDOR_VERIFICA_LETRA
   ├─ Si letra EN palabra:
   │  ├─ Agrega a letras_adivinadas
   │  ├─ Envía "letra_correcta"
   │  └─ Si completa → FINALIZAR_RONDA(ganador=adivinador)
   └─ Si letra NO EN palabra:
      ├─ errores++
      ├─ Envía "letra_incorrecta"
      └─ Si errores == 8 → FINALIZAR_RONDA(ganador=rival)

6. FINALIZAR_RONDA
   ├─ Suma punto al ganador
   ├─ Si ganador.puntos == 5 → FINALIZAR_JUEGO
   └─ Sino:
      ├─ Invierte roles (jugador_adivinando)
      ├─ ronda_actual++
      └─ Vuelve a paso 1 (después de 3 segundos)

7. FINALIZAR_JUEGO
   ├─ Muestra modal de victoria/derrota
   └─ Botón "Volver al Menú"
```

## Gestión de Desconexiones

```python
async def disconnect(self, close_code):
    estado = self.salas_estado.get(self.codigo_sala)
    
    if estado:
        # Marcar como desconectado
        estado['desconectado'] = self.jugador_id
        
        # Notificar desconexión
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'jugador_desconectado',
                'jugador_id': self.jugador_id
            }
        )
```

```javascript
// Cliente - Contador de reconexión
function iniciarContadorReconexion() {
    let tiempo = 20;
    reconexionInterval = setInterval(() => {
        tiempo--;
        if (tiempo <= 0) {
            // Victoria automática para el jugador conectado
            juegoTerminado({
                ganador: miId,
                puntos: { jugador1: 5, jugador2: 0 }
            });
        }
    }, 1000);
}
```

## SVG del Ahorcado

### Estructura

```html
<svg width="200" height="250">
    <!-- Base (siempre visible) -->
    <g id="base" class="show">
        <line x1="10" y1="230" x2="150" y2="230" />
    </g>
    
    <!-- 8 partes ocultas por defecto -->
    <g id="parte-1" class="hidden"> <!-- Horca --> </g>
    <g id="parte-2" class="hidden"> <!-- Cuerda --> </g>
    <g id="parte-3" class="hidden"> <!-- Cabeza --> </g>
    <g id="parte-4" class="hidden"> <!-- Torso --> </g>
    <g id="parte-5" class="hidden"> <!-- Brazo izq --> </g>
    <g id="parte-6" class="hidden"> <!-- Brazo der --> </g>
    <g id="parte-7" class="hidden"> <!-- Pierna izq --> </g>
    <g id="parte-8" class="hidden"> <!-- Pierna der --> </g>
</svg>
```

### Mostrar Partes

```javascript
function mostrarParteAhorcado(errores) {
    if (errores > 0 && errores <= 8) {
        document.getElementById(`parte-${errores}`)
            .classList.remove('hidden');
        document.getElementById(`parte-${errores}`)
            .classList.add('show');
    }
}
```

```css
.hidden { display: none; }
.show { display: block; }
```

## Timer del Cliente

```javascript
function iniciarTimer(segundos) {
    let tiempo = segundos;
    actualizarTimerDisplay(tiempo);
    
    timerInterval = setInterval(() => {
        tiempo--;
        actualizarTimerDisplay(tiempo);
        
        if (tiempo <= 0) {
            detenerTimer();
            // El jugador pierde por tiempo
        }
    }, 1000);
}

function actualizarTimerDisplay(segundos) {
    const minutos = Math.floor(segundos / 60);
    const segs = segundos % 60;
    document.getElementById('timer').textContent = 
        `${minutos.toString().padStart(2, '0')}:${segs.toString().padStart(2, '0')}`;
}
```

## Base de Datos

### Modelo Sala

```python
class Sala(models.Model):
    codigo = models.CharField(max_length=6, unique=True, primary_key=True)
    creada_en = models.DateTimeField(auto_now_add=True)
    jugadores_conectados = models.IntegerField(default=0)
    
    @classmethod
    def generar_codigo(cls):
        while True:
            codigo = ''.join(random.choices(
                string.ascii_uppercase + string.digits, 
                k=6
            ))
            if not cls.objects.filter(codigo=codigo).exists():
                return codigo
```

### SQL Generado

```sql
CREATE TABLE "game_sala" (
    "codigo" varchar(6) NOT NULL PRIMARY KEY,
    "creada_en" datetime NOT NULL,
    "jugadores_conectados" integer NOT NULL
);
```

## Optimizaciones Futuras

### 1. Usar Redis para Channel Layers
```python
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [('127.0.0.1', 6379)],
        },
    },
}
```

### 2. Persistir Estado del Juego
Actualmente el estado está en memoria. Para producción, considera:
- Redis para estado en tiempo real
- PostgreSQL para historial de partidas

### 3. Limpieza de Salas Inactivas
```python
# management/commands/limpiar_salas.py
from django.core.management.base import BaseCommand
from game.models import Sala
from django.utils import timezone
from datetime import timedelta

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        # Eliminar salas con más de 1 hora
        hace_una_hora = timezone.now() - timedelta(hours=1)
        Sala.objects.filter(creada_en__lt=hace_una_hora).delete()
```

### 4. Rate Limiting
Agregar límites de tasa para prevenir spam:
```python
# En consumers.py
from django.core.cache import cache

async def receive(self, text_data):
    key = f'rate_limit_{self.channel_name}'
    if cache.get(key):
        return  # Ignorar si está en cooldown
    
    cache.set(key, True, 0.5)  # 500ms cooldown
    # ... resto del código
```

## Testing

### Test de Consumer

```python
# tests.py
from channels.testing import WebsocketCommunicator
from django.test import TestCase
from game.consumers import GameConsumer

class GameConsumerTest(TestCase):
    async def test_connection(self):
        communicator = WebsocketCommunicator(
            GameConsumer.as_asgi(),
            "/ws/sala/TEST01/"
        )
        connected, subprotocol = await communicator.connect()
        assert connected
        await communicator.disconnect()
```

## Monitoreo

### Logs importantes

```python
# consumers.py
import logging
logger = logging.getLogger(__name__)

async def connect(self):
    logger.info(f"Jugador conectado a sala {self.codigo_sala}")
    # ...

async def disconnect(self, close_code):
    logger.warning(f"Jugador desconectado: {self.jugador_id} (code: {close_code})")
    # ...
```

### Métricas a monitorear
- Número de salas activas
- Jugadores conectados simultáneamente
- Tiempo promedio de partida
- Rate de desconexiones
- Errores de WebSocket

---

¿Dudas? Revisa el código fuente o contacta al autor del proyecto.
