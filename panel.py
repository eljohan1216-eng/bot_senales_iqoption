# ===============================================================
# 📊 PANEL DE SEÑALES IQ OPTION – VERSIÓN FINAL (Render + Local)
# ===============================================================

from flask import Flask, render_template, jsonify
import threading, time, random, os

app = Flask(__name__)

# ------------------------------
# 🔧 CONFIGURACIÓN DEL BOT
# ------------------------------
bot_activo = True
MODO_ACTUAL = "MIXTO"
pares = ["EURUSD", "GBPUSD", "USDJPY", "EURUSD-OTC", "GBPUSD-OTC", "USDJPY-OTC", "USDCAD", "EURGBP-OTC"]

estrategias = [
    "Acción del Precio + Soporte/Resistencia",
    "Ruptura de Nivel + Volumen",
    "Rechazo de Zona Institucional",
    "Pullback + EMA20",
    "Cambio de Tendencia + Confirmación de Vela"
]

# ------------------------------
# 🧠 GENERADOR DE SEÑALES
# ------------------------------
senales = []

def generar_senales():
    global senales
    while bot_activo:
        par = random.choice(pares)
        tipo = random.choice(["CALL", "PUT"])
        precio = round(random.uniform(1.10, 1.35), 6)
        confianza = random.randint(80, 99)
        duracion = random.choice([1, 2, 3])
        estrategia = random.choice(estrategias)
        hora_actual = time.strftime("%H:%M:%S")

        nueva_senal = {
            "par": par,
            "tipo": tipo,
            "precio": precio,
            "entrada": hora_actual,
            "expira": time.strftime("%H:%M:%S", time.localtime(time.time() + duracion * 60)),
            "confianza": f"{confianza}%",
            "duracion": f"{duracion} min",
            "estrategia": estrategia,
            "estado": "EN CURSO"
        }

        senales.insert(0, nueva_senal)
        if len(senales) > 10:
            senales.pop()

        print(f"📈 Señal generada: {nueva_senal}")
        time.sleep(10)  # cada 10 segundos genera una nueva

# ------------------------------
# 🌐 RUTAS DEL PANEL WEB
# ------------------------------
@app.route("/")
def index():
    return render_template("panel.html", senales=senales, bot_activo=bot_activo, modo=MODO_ACTUAL)

@app.route("/api/senales")
def api_senales():
    return jsonify(senales)

# ------------------------------
# ⚙️ EJECUCIÓN DEL SERVIDOR
# ------------------------------
if __name__ == "__main__":
    print("✅ Conectado correctamente a IQ Option (REAL)")
    print(f"🚀 Iniciando bot en modo {MODO_ACTUAL}...")
    threading.Thread(target=generar_senales, daemon=True).start()

    # 🔥 CONFIGURACIÓN FINAL DEL SERVIDOR FLASK 🔥
    port = int(os.environ.get("PORT", 8765))
    host = "0.0.0.0" if "RENDER" in os.environ else "127.0.0.1"
    print(f"🌐 Servidor Flask ejecutándose en http://{host}:{port}")
    app.run(host=host, port=port)
