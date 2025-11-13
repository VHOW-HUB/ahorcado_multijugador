#!/bin/bash

echo "🎮 Iniciando Ahorcado Multijugador..."
echo ""

# Verificar si Django está instalado
if ! python3 -c "import django" &> /dev/null; then
    echo "⚠️  Django no está instalado. Instalando dependencias..."
    pip install django channels daphne
fi

echo "✅ Dependencias verificadas"
echo ""

# Aplicar migraciones
echo "📦 Aplicando migraciones..."
python3 manage.py migrate --noinput

echo ""
echo "🚀 Iniciando servidor en http://localhost:8000"
echo ""
echo "📋 Instrucciones:"
echo "   1. Abre http://localhost:8000 en tu navegador"
echo "   2. Crea una sala o únete con un código"
echo "   3. Comparte el código con un amigo"
echo "   4. ¡A jugar!"
echo ""
echo "⏹️  Para detener el servidor, presiona CTRL+C"
echo ""

# Iniciar servidor con Daphne
python3 manage.py runserver 0.0.0.0:8000
