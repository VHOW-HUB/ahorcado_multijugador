# 📁 ÍNDICE DE ARCHIVOS DEL PROYECTO

## 🚀 Archivos de Inicio Rápido

| Archivo | Descripción | Cómo usar |
|---------|-------------|-----------|
| `start.sh` | Script de inicio automático | `./start.sh` |
| `INICIO_RAPIDO.md` | Guía de inicio rápido | Leer primero |
| `requirements.txt` | Dependencias Python | `pip install -r requirements.txt` |
| `manage.py` | CLI de Django | `python manage.py runserver` |

## 📚 Documentación

| Archivo | Contenido | Para quién |
|---------|-----------|------------|
| `README.md` | Documentación completa del proyecto | Todos |
| `CARACTERISTICAS.md` | Lista de todas las funcionalidades | Revisar implementación |
| `DOCUMENTACION_TECNICA.md` | Detalles técnicos y arquitectura | Desarrolladores |
| `PALABRAS_SUGERIDAS.md` | Lista de palabras para jugar | Jugadores |

## ⚙️ Configuración del Proyecto

```
ahorcado_game/
├── ahorcado_game/              # Carpeta de configuración Django
│   ├── __init__.py            # Marca como paquete Python
│   ├── asgi.py                # ⭐ Configuración ASGI + Channels
│   ├── settings.py            # ⭐ Settings: Apps, Channels, DB
│   ├── urls.py                # URLs principales del proyecto
│   └── wsgi.py                # Configuración WSGI (no usado)
```

**Archivos importantes en esta carpeta:**
- `asgi.py` - Configura el routing de WebSockets
- `settings.py` - Añade 'daphne', 'channels', 'game' a INSTALLED_APPS

## 🎮 Aplicación del Juego

```
game/
├── __init__.py                # Marca como paquete Python
├── admin.py                   # Admin de Django (vacío)
├── apps.py                    # Config de la app
├── consumers.py               # ⭐⭐⭐ LÓGICA WEBSOCKET (más importante)
├── models.py                  # ⭐ Modelo Sala
├── routing.py                 # ⭐ Routing WebSocket
├── urls.py                    # ⭐ URLs de la app
├── views.py                   # ⭐ Vistas Django
├── tests.py                   # Tests (vacío por ahora)
├── migrations/
│   ├── __init__.py
│   └── 0001_initial.py       # Migración de Sala
└── templates/game/            # Templates HTML
    ├── base.html              # ⭐ Template base con estilos
    ├── index.html             # ⭐ Menú principal
    ├── sala.html              # ⭐⭐⭐ Pantalla del juego (más importante)
    └── sala_no_existe.html    # Error 404 de sala
```

### 🌟 Archivos Clave

#### 1. `consumers.py` (300+ líneas)
**QUÉ HACE:**
- Maneja todas las conexiones WebSocket
- Gestiona el estado del juego en memoria
- Procesa mensajes de jugadores
- Controla la lógica de rondas y puntos

**FUNCIONES PRINCIPALES:**
- `connect()` - Jugador se conecta
- `disconnect()` - Jugador se desconecta
- `receive()` - Recibe mensajes del cliente
- `iniciar_juego()` - Comienza el juego con 2 jugadores
- `procesar_palabra()` - Guarda palabra secreta
- `procesar_letra()` - Verifica letra adivinada
- `finalizar_ronda()` - Termina ronda y suma puntos
- `finalizar_juego()` - Termina juego (5 puntos)

#### 2. `sala.html` (400+ líneas)
**QUÉ HACE:**
- Interfaz completa del juego
- SVG del ahorcado con 8 partes
- Teclado virtual interactivo
- Timer, marcador, mensajes
- Lógica JavaScript del cliente

**SECCIONES:**
- Estilos CSS (150 líneas)
- HTML estructura (100 líneas)
- JavaScript WebSocket (150 líneas)

#### 3. `models.py`
**QUÉ HACE:**
- Define el modelo Sala
- Genera códigos únicos de 6 caracteres

**MODELO:**
```python
class Sala:
    codigo = CharField(max_length=6, unique=True)
    creada_en = DateTimeField(auto_now_add=True)
    jugadores_conectados = IntegerField(default=0)
```

#### 4. `views.py`
**QUÉ HACE:**
- Vista para menú principal
- Vista para crear sala
- Vista para unirse a sala
- Vista para pantalla de juego

**VISTAS:**
- `index()` - Menú principal
- `crear_sala()` - Genera código y crea sala
- `unirse_sala()` - Valida código y redirige
- `sala()` - Renderiza pantalla de juego

## 📊 Flujo de Archivos

### Flujo HTTP (Páginas normales)
```
Usuario visita URL
    ↓
urls.py (proyecto) → game/urls.py
    ↓
game/views.py
    ↓
game/templates/game/*.html
    ↓
Navegador del usuario
```

### Flujo WebSocket (Tiempo real)
```
Cliente abre WebSocket
    ↓
asgi.py → game/routing.py
    ↓
game/consumers.py
    ↓
Lógica del juego
    ↓
Broadcasting a todos los jugadores
```

## 🎨 Recursos Visuales

### SVG del Ahorcado
Ubicación: `game/templates/game/sala.html` (líneas 140-190)

```html
<svg width="200" height="250">
  <g id="base">...</g>        <!-- Siempre visible -->
  <g id="parte-1">...</g>     <!-- Error 1: Horca -->
  <g id="parte-2">...</g>     <!-- Error 2: Cuerda -->
  <g id="parte-3">...</g>     <!-- Error 3: Cabeza -->
  <g id="parte-4">...</g>     <!-- Error 4: Torso -->
  <g id="parte-5">...</g>     <!-- Error 5: Brazo izq -->
  <g id="parte-6">...</g>     <!-- Error 6: Brazo der -->
  <g id="parte-7">...</g>     <!-- Error 7: Pierna izq -->
  <g id="parte-8">...</g>     <!-- Error 8: Pierna der -->
</svg>
```

### Estilos CSS
Ubicación: `game/templates/game/base.html` + `sala.html`

**Colores principales:**
- Púrpura primario: `#667eea`
- Púrpura secundario: `#764ba2`
- Rosa: `#f5576c`
- Verde éxito: `#28a745`
- Rojo error: `#dc3545`

## 🗂️ Base de Datos

**Archivo:** `db.sqlite3`

**Tablas:**
- `game_sala` - Almacena códigos de salas creadas
- Tablas Django por defecto (auth, sessions, etc.)

**Nota:** El estado del juego NO está en la base de datos, está en memoria (variable `salas_estado` en `consumers.py`)

## 📦 Dependencias

**Archivo:** `requirements.txt`

```
Django>=5.2.0          # Framework web
channels>=4.3.0        # WebSockets
channels-redis>=4.3.0  # Backend para Channels
daphne>=4.2.0          # Servidor ASGI
```

## 🔍 Archivos que NO debes modificar (generados automáticamente)

- `db.sqlite3` - Base de datos
- `game/__pycache__/` - Bytecode compilado
- `ahorcado_game/__pycache__/` - Bytecode compilado
- `game/migrations/0001_initial.py` - Migración generada

## 📝 Archivos que SÍ puedes modificar fácilmente

### Para cambiar el diseño:
- `game/templates/game/base.html` - Estilos globales
- `game/templates/game/sala.html` - Estilos del juego

### Para cambiar la lógica del juego:
- `game/consumers.py` - Lógica del servidor
- `game/templates/game/sala.html` (JavaScript) - Lógica del cliente

### Para cambiar tiempos y reglas:
- `game/consumers.py` línea 18: `'tiempo_restante': 90` (segundos por ronda)
- `game/consumers.py` línea 20: `'tiempo_espera_reconexion': 20` (segundos para reconectar)
- `game/consumers.py` línea 155: `if estado['puntos'][ganador] >= 5:` (puntos para ganar)
- `game/consumers.py` línea 108: `if estado['errores'] >= 8:` (errores máximos)

## 🎯 Archivos por Importancia

### ⭐⭐⭐ CRÍTICOS (no tocar sin saber)
1. `game/consumers.py` - Toda la lógica del juego
2. `game/templates/game/sala.html` - Interfaz completa
3. `ahorcado_game/asgi.py` - Configuración WebSocket

### ⭐⭐ IMPORTANTES
4. `ahorcado_game/settings.py` - Configuración Django
5. `game/models.py` - Base de datos
6. `game/views.py` - Vistas
7. `game/urls.py` - Rutas

### ⭐ ÚTILES
8. `game/templates/game/index.html` - Menú
9. `game/templates/game/base.html` - Estilos base
10. `game/routing.py` - Routing WebSocket

## 📋 Checklist de Archivos

✅ Todos los archivos necesarios están presentes
✅ Documentación completa creada
✅ Templates HTML con estilos
✅ Lógica WebSocket implementada
✅ Base de datos configurada
✅ Scripts de inicio creados
✅ README detallado
✅ Guías de inicio rápido
✅ Documentación técnica

## 🎓 Orden de Lectura Recomendado

**Para empezar rápido:**
1. `INICIO_RAPIDO.md`
2. `README.md` (sección "Cómo jugar")
3. Ejecutar `./start.sh`

**Para entender el proyecto:**
1. `README.md` (completo)
2. `CARACTERISTICAS.md`
3. Ver `game/templates/game/index.html` (simple)
4. Ver `game/views.py` (lógica básica)
5. Ver `game/consumers.py` (lógica WebSocket)
6. Ver `game/templates/game/sala.html` (interfaz)

**Para modificar o extender:**
1. `DOCUMENTACION_TECNICA.md`
2. Código fuente con comentarios
3. Probar cambios en desarrollo

---

**Total de archivos:** 27 archivos (13 Python, 4 HTML, 5 Markdown, 2 config, 3 otros)

**Líneas de código aproximadas:**
- Python: ~600 líneas
- HTML/CSS: ~800 líneas
- JavaScript: ~350 líneas
- Documentación: ~2000 líneas
- **Total: ~3750 líneas**

¡Proyecto completo y bien documentado! 🎉
