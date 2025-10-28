#!/bin/bash
echo "🧹 Cerrando procesos viejos de Python..."
killall python3 >/dev/null 2>&1 || true
sleep 1

echo "🚀 Iniciando Panel de Señales..."
python3 panel.py &
sleep 3

echo "📡 Iniciando Bot en MODO REAL..."
python3 bot_iq.py &
sleep 2

echo "✅ Todo está corriendo. Abre tu navegador en:"
echo "👉 http://127.0.0.1:8765"
