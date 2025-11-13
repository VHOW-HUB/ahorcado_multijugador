# 🎮 Ahorcado Multijugador - Django WebSockets

Juego del ahorcado en tiempo real para 2 jugadores usando Django y WebSockets (Django Channels).

## 📋 Características

- ✅ Juego multijugador en tiempo real sin necesidad de registro
- ✅ Sistema de salas con códigos únicos (6 caracteres)
- ✅ Timer de 90 segundos por ronda
- ✅ 8 oportunidades para adivinar (con dibujo progresivo del ahorcado)
- ✅ Partidas al mejor de 5 puntos
- ✅ Sistema de reconexión (20 segundos de espera)
- ✅ Diseño minimalista estilo "Hill Climb" con SVG
- ✅ Mínimo JavaScript necesario

## 🚀 Instalación

### 1. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 2. Ejecutar migraciones

```bash
python manage.py migrate
```

### 3. Iniciar el servidor

```bash
python manage.py runserver
```

El servidor estará disponible en: `http://127.0.0.1:8000/`

## 🎯 Cómo Jugar

1. **Crear una sala**: Un jugador crea una nueva sala y obtiene un código de 6 caracteres
2. **Unirse a la sala**: El segundo jugador ingresa el código para unirse
3. **Asignación aleatoria**: El sistema asigna aleatoriamente quién adivina primero
4. **Escribir palabra**: El jugador que no adivina escribe una palabra secreta
5. **Adivinar**: El otro jugador tiene 90 segundos y 8 intentos para adivinar
6. **Intercambio de roles**: Los roles se invierten automáticamente en cada ronda
7. **Victoria**: El primer jugador en ganar 5 rondas gana el juego

## 📁 Estructura del Proyecto

```
ahorcado_game/
├── ahorcado_game/          # Configuración principal
│   ├── settings.py         # Configuración de Django y Channels
│   ├── asgi.py            # Configuración ASGI para WebSockets
│   └── urls.py            # URLs principales
├── game/                   # App del juego
│   ├── consumers.py       # Lógica WebSocket (GameConsumer)
│   ├── models.py          # Modelo de Sala
│   ├── views.py           # Vistas de Django
│   ├── routing.py         # Rutas WebSocket
│   └── templates/         # Plantillas HTML
│       └── game/
│           ├── base.html         # Template base
│           ├── index.html        # Menú principal
│           ├── sala.html         # Sala de juego
│           └── sala_no_existe.html
├── manage.py
├── requirements.txt
└── README.md
```

## 🛠️ Tecnologías Utilizadas

- **Django 5.2.8** - Framework web
- **Django Channels 4.2.2** - WebSockets para comunicación en tiempo real
- **Daphne 4.1.2** - Servidor ASGI
- **SQLite** - Base de datos (para guardar códigos de salas)
- **Vanilla JavaScript** - Mínimo JS en el cliente
- **SVG** - Gráficos del ahorcado

## ⚙️ Configuración

El proyecto usa:
- **InMemoryChannelLayer** para desarrollo (para producción usar Redis)
- **Idioma**: Español (es-es)
- **Debug**: True (cambiar a False en producción)

## 🎨 Diseño

- Estilo minimalista inspirado en "Hill Climb Racing"
- Colores principales: Gradiente morado (#667eea → #764ba2)
- SVG para el dibujo del ahorcado (8 partes)
- Responsive y optimizado para navegadores modernos

## 📝 Reglas del Juego

- **Tiempo**: 90 segundos por ronda
- **Intentos**: 8 errores máximo
- **Puntos**: Al mejor de 5 puntos
- **Desconexión**: 20 segundos de espera antes de dar victoria automática
- **Roles**: Se intercambian automáticamente cada ronda
- **Palabra mínima**: 3 letras

## 🐛 Troubleshooting

### Error: "WebSocket connection failed"
- Verifica que el servidor esté corriendo
- Asegúrate de usar el protocolo correcto (ws:// o wss://)

### Error: "Sala no encontrada"
- El código debe ser exacto (6 caracteres)
- Las salas son de un solo uso

### El timer no se sincroniza
- El timer se controla desde el servidor para evitar trampas
- Se envían actualizaciones cada 5 segundos

## 📦 Producción

Para producción, considera:

1. Cambiar `DEBUG = False` en settings.py
2. Usar Redis como backend de Channels:
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
3. Configurar ALLOWED_HOSTS
4. Usar un servidor de producción (Daphne, Uvicorn)
5. Configurar HTTPS para WebSocket seguro (wss://)

## 📄 Licencia

Proyecto educativo - Curso de Python Web con Django

## 👨‍💻 Autor

Desarrollado como proyecto de curso de Django
