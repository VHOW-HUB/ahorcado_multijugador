# 🚀 INICIO RÁPIDO

## Opción 1: Script automático (Linux/Mac)
```bash
./start.sh
```

## Opción 2: Manual

### 1. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 2. Iniciar servidor
```bash
python manage.py runserver
```

### 3. Abrir navegador
```
http://localhost:8000
```

## 🎮 Probar el juego

Para probar en local con un solo ordenador:

1. Abre **dos ventanas del navegador** (o una en modo incógnito)
2. En la primera ventana:
   - Haz clic en "Crear Nueva Sala"
   - Copia el código que aparece
3. En la segunda ventana:
   - Ve a http://localhost:8000
   - Introduce el código de la sala
   - Haz clic en "Unirse a Sala"
4. ¡Ya puedes jugar contigo mismo para probar!

## ⚠️ Importante

- Necesitas **Python 3.8 o superior**
- El servidor debe estar corriendo para que el juego funcione
- No cierres la terminal donde se ejecuta el servidor

## 🐛 Si algo no funciona

1. Verifica que el puerto 8000 esté libre:
   ```bash
   lsof -i :8000
   ```

2. Reinstala las dependencias:
   ```bash
   pip install --upgrade -r requirements.txt
   ```

3. Limpia la base de datos:
   ```bash
   rm db.sqlite3
   python manage.py migrate
   ```
