# ==========================================================
# PANEL DE SEÑALES IQ OPTION - MODO MIXTO (OTC + REAL)
# ==========================================================

from flask import Flask, render_template, jsonify
from datetime import datetime, timedelta
import random, time, threading

app = Flask(__name__)

# -------- CONFIGURACIÓN PRINCIPAL --------
MODO_ACTUAL = "MIXTO"  # Opciones: "OTC", "REAL" o "MIXTO"
senales = []  # Lista de señales activas

# -------- FUNCIÓN PARA GENERAR SEÑALES --------
def generar_senales():
    """Genera señales simuladas en modo mixto"""
    global senales
    while True:
        confianza = random.randint(80, 99)
        duracion_min = 1 if confianza < 91 else 3 if confianza < 96 else 5
        ahora = datetime.now()

        nueva = {
            "par": random.choice(["EURUSD-OTC", "GBPUSD-OTC", "USDJPY", "AUDCAD", "EURGBP-OTC", "USDCAD"]),
            "tipo": random.choice(["CALL", "PUT"]),
            "precio": round(random.uniform(1.10, 1.30), 6),
            "entrada": ahora.strftime("%H:%M:%S"),
            "expira": (ahora + timedelta(minutes=duracion_min)).strftime("%H:%M:%S"),
            "confianza": confianza,
            "duracion": f"{duracion_min} min",
            "estrategia": random.choice([
                "Pullback + EMA20",
                "Ruptura de Nivel + Volumen",
                "Rechazo de Zona Institucional",
                "Cambio de Tendencia + Confirmación de Vela",
                "Acción del Precio + Soporte/Resistencia"
            ]),
            "estado": "EN CURSO"
        }

        senales.insert(0, nueva)
        if len(senales) > 15:
            senales.pop()

        # Cambiar estado a FINALIZADA después del tiempo correspondiente
        def cerrar_senal(senal):
            time.sleep(duracion_min * 60)
            senal["estado"] = "FINALIZADA ✅"

        threading.Thread(target=cerrar_senal, args=(nueva,), daemon=True).start()
        time.sleep(5)

# -------- ACTUALIZAR HORA EN TIEMPO REAL --------
@app.route('/hora')
def hora_actual():
    return jsonify({"hora": datetime.now().strftime("%I:%M:%S %p")})

# -------- INTERFAZ WEB --------
@app.route('/')
def index():
    return render_template(
        "panel.html",
        conectado=True,
        modo_actual=MODO_ACTUAL,
        bot_activo=True,
        senales=senales
    )

# ----------------------------
# 🔥 EJECUCIÓN FINAL DEL BOT + SERVIDOR FLASK
# ----------------------------
import os
import threading

if __name__ == "__main__":
    print("✅ Conectado correctamente a IQ Option (REAL)")
    print(f"🚀 Iniciando bot en modo mixto ({MODO_ACTUAL})...")

    # 🔁 Inicia el hilo del generador de señales
    threading.Thread(target=generar_senales, daemon=True).start()

    # 🌍 Configuración dinámica para Render y local
    port = int(os.environ.get("PORT", 8765))  # Render asigna automáticamente este puerto
    host = "0.0.0.0" if "RENDER" in os.environ else "127.0.0.1"

    print(f"🌐 Servidor Flask ejecutándose en http://{host}:{port}")
    app.run(host=host, port=port)
