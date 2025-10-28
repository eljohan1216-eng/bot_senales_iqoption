#!/bin/bash
echo "🚀 Iniciando todo el sistema..."
cd ~/Desktop/bot_senales
pkill -f "python3 panel.py" 2>/dev/null
pkill -f "python3 bot_iq.py" 2>/dev/null
sleep 2
echo "✅ Procesos anteriores detenidos"
python3 bot_iq.py > /tmp/bot_log.txt 2>&1 &
python3 panel.py > /tmp/panel_log.txt 2>&1 &
sleep 2
echo "✅ Todo listo, abre tu navegador en: http://127.0.0.1:8765"
