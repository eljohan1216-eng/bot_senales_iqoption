#!/bin/bash
echo "🚀 Iniciando Panel de Señales OTC..."
cd ~/Desktop/bot_senales

# 🧹 Detiene procesos viejos si existen
killall ngrok 2>/dev/null
pkill -f "python3 panel.py" 2>/dev/null

# ⏳ Espera un poco para liberar el puerto
sleep 2

# ▶️ Inicia el panel Flask en segundo plano
echo "✅ Iniciando servidor local (Flask)..."
python3 panel.py > /dev/null 2>&1 &

# ⏱ Espera unos segundos antes de lanzar ngrok
sleep 5

# 🌍 Inicia ngrok en el puerto 5002
echo "🌐 Iniciando Ngrok..."
ngrok http 5002 > /tmp/ngrok_log.txt &

# 🔗 Muestra mensaje final
sleep 5
echo ""
echo "---------------------------------------------"
echo "🔎 Abre el enlace de Ngrok que ves en su ventana."
echo "   (Si no lo ves, ejecuta: ngrok http 5002)"
echo "---------------------------------------------"
echo "❌ Para detener todo, usa:"
echo "killall ngrok; pkill -f 'python3 panel.py'"
echo "---------------------------------------------"#!/bin/bash
echo "🚀 Iniciando Panel de Señales OTC..."
cd ~/Desktop/bot_senales

# 🔹 Detiene procesos viejos si existen
killall ngrok 2>/dev/null
pkill -f "python3 panel.py" 2>/dev/null

# 🔹 Espera un poco para liberar el puerto
sleep 2

# 🔹 Inicia el panel Flask en segundo plano
echo "✅ Iniciando servidor local (Flask)..."
python3 panel.py > /dev/null 2>&1 &

# 🔹 Espera unos segundos antes de lanzar ngrok
sleep 5

# 🔹 Inicia ngrok y guarda su log
echo "🌍 Iniciando Ngrok..."
ngrok http 5001 > /tmp/ngrok_log.txt &
sleep 5

# 🔹 Extrae el enlace público
URL=$(grep -o "https://[a-zA-Z0-9.-]*\.ngrok-free\.dev" /tmp/ngrok_log.txt | head -n 1)

if [ -z "$URL" ]; then
    echo "⚠️ No se pudo obtener el enlace de ngrok. Verifica si está conectado."
else
    echo "✅ Tu panel está disponible en: $URL"
    echo "$URL" | pbcopy
    echo "📋 Enlace copiado al portapapeles."
fi

echo "------------------------------------------"
echo "Para detener todo, ejecuta:"
echo "killall ngrok; pkill -f 'python3 panel.py'"
echo "------------------------------------------"
#!/bin/bash
echo "🚀 Iniciando Panel de Señales OTC..."
cd ~/Desktop/bot_senales

# 🔹 Detiene procesos viejos si existen
killall ngrok 2>/dev/null
pkill -f "python3 panel.py" 2>/dev/null

# 🔹 Espera un poco para liberar el puerto
sleep 2

# 🔹 Inicia el panel Flask en segundo plano
echo "✅ Iniciando servidor local (Flask)..."
python3 panel.py > /dev/null 2>&1 &

# 🔹 Espera unos segundos antes de lanzar ngrok
sleep 5

# 🔹 Inicia ngrok
echo "🌍 Iniciando Ngrok..."
ngrok http 5001 > /tmp/ngrok_log.txt &
sleep 5

# 🔹 Extrae el enlace público de ngrok
URL=$(grep -o "https://[a-zA-Z0-9.-]*\.ngrok-free\.app" /tmp/ngrok_log.txt | head -n 1)

if [ -z "$URL" ]; then
    echo "⚠️ No se pudo obtener el enlace de ngrok. Verifica si está conectado."
else
    echo "✅ Tu panel está disponible en: $URL"
    echo "$URL" | pbcopy
    echo "📋 Enlace copiado al portapapeles."
fi

echo "------------------------------------------"
echo "Para detener todo, ejecuta:"
echo "killall ngrok; pkill -f 'python3 panel.py'"
echo "------------------------------------------"#!/bin/bash
killall ngrok python3 2>/dev/null

echo "🚀 Iniciando Panel de Señales OTC..."

# Activar entorno virtual si existe
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Iniciar panel en segundo plano
python3 panel.py &
PANEL_PID=$!
echo "✅ Panel ejecutándose (PID: $PANEL_PID)"

# Esperar unos segundos antes de iniciar ngrok
sleep 3

# Iniciar túnel ngrok
ngrok http 5001 > /tmp/ngrok.log &
NGROK_PID=$!
echo "🌍 Ngrok iniciado (PID: $NGROK_PID)"
sleep 5

# Extraer el enlace público de ngrok
NGROK_URL=$(grep -o "https://[a-zA-Z0-9.-]*\.ngrok-free\.app" /tmp/ngrok.log | head -n 1)

if [ -n "$NGROK_URL" ]; then
    echo "🔗 Tu panel está disponible en: $NGROK_URL"
    echo "$NGROK_URL" | pbcopy
    echo "📋 Enlace copiado automáticamente al portapapeles ✅"
else
    echo "⚠️ No se pudo obtener el enlace de ngrok. Verifica si está corriendo correctamente."
fi

echo "---------------------------------------------"
echo "💡 Puedes abrir tu panel desde cualquier dispositivo con el enlace anterior."
echo "📊 Para detener todo, usa:"
echo "   kill $PANEL_PID $NGROK_PID"
echo "---------------------------------------------"

# Mantener el script activo para ver logs
wait
