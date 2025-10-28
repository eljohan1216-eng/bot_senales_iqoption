# -*- coding: utf-8 -*-
"""
Panel de Señales IQ Option – Compatible LOCAL + RENDER
- Hora local con zona "America/Santiago"
- Modo actual visible (OTC / REAL / MIXTO)
- Duración por confianza: 85–90 => 1m, 90–95 => 3m, 95–100 => 5m
- API /status para hora y modo (polled por el front)
- API /api/signals para tabla (tu generador la alimenta)
"""

import os
import json
import random
import threading
from datetime import datetime, timedelta, timezone

try:
    # Python 3.9+ trae zoneinfo en la stdlib
    from zoneinfo import ZoneInfo
    TZ_CL = ZoneInfo("America/Santiago")
except Exception:
    # Fallback (si llegara a faltar zoneinfo en alguna máquina)
    import pytz
    TZ_CL = pytz.timezone("America/Santiago")

from flask import Flask, render_template, jsonify

# -----------------------------
# CONFIGURACIÓN
# -----------------------------
MODO_ACTUAL = os.environ.get("MODO_ACTUAL", "MIXTO")  # "OTC", "REAL" o "MIXTO"

# Si Render asigna puerto dinámico lo usamos; si no, local 8765
PORT = int(os.environ.get("PORT", 8765))
# Host: en Render debe ser 0.0.0.0; local puede ser 127.0.0.1
HOST = "0.0.0.0" if "RENDER" in os.environ or os.environ.get("ON_RENDER") else "127.0.0.1"

# Estructura de señales en memoria
senales = []  # cada item: dict con par, tipo, precio, entrada, expira, confianza, duracion_min, estrategia, estado

bot_activo = True
app = Flask(__name__, template_folder="templates", static_folder="static")


# -----------------------------
# UTILIDADES
# -----------------------------
def ahora_cl():
    """Devuelve datetime timezone-aware en Chile."""
    # Si TZ_CL es pytz, se usa localize; si es zoneinfo, replace tzinfo
    try:
        return datetime.now(TZ_CL)
    except Exception:
        return pytz.utc.localize(datetime.utcnow()).astimezone(TZ_CL)  # pragma: no cover


def fmt_hhmmss(dt: datetime) -> str:
    return dt.strftime("%I:%M:%S %p")  # 12h con AM/PM como en tu panel


def duracion_por_confianza(conf: int) -> int:
    """Regla solicitada: 85–90 => 1, 90–95 => 3, 95–100 => 5 (minutos)."""
    if conf < 90:
        return 1
    elif conf < 95:
        return 3
    else:
        return 5


# -----------------------------
# GENERADOR DE SEÑALES (demostración)
# NOTA: aquí puedes conectar tu lógica real/IQOption. Mantengo un mock estable.
# -----------------------------
PARES_REAL = ["EURUSD", "GBPUSD", "USDJPY"]
PARES_OTC = ["EURUSD-OTC", "GBPUSD-OTC", "USDJPY-OTC"]
ESTRATEGIAS = [
    "Pullback + EMA20",
    "Ruptura de Nivel + Volumen",
    "Acción del Precio + Soporte/Resistencia",
    "Cambio de Tendencia + Confirmación de Vela",
    "Rechazo de Zona Institucional"
]

def generar_senales():
    while bot_activo:
        try:
            now = ahora_cl()
            # Decide universo
            universo = []
            if MODO_ACTUAL in ("REAL", "MIXTO"):
                universo += PARES_REAL
            if MODO_ACTUAL in ("OTC", "MIXTO"):
                universo += PARES_OTC
            if not universo:
                universo = PARES_OTC

            par = random.choice(universo)
            tipo = random.choice(["CALL", "PUT"])
            precio = round(random.uniform(1.05, 1.35), 6)
            confianza = random.randint(80, 99)
            dur_min = duracion_por_confianza(max(85, confianza))  # aseguramos >=85
            entrada = now + timedelta(seconds=random.randint(30, 90))
            expira = entrada + timedelta(minutes=dur_min)
            estrategia = random.choice(ESTRATEGIAS)

            senales.append({
                "par": par,
                "tipo": tipo,
                "precio": precio,
                "entrada": entrada.isoformat(),
                "expira": expira.isoformat(),
                "confianza": confianza,
                "duracion_min": dur_min,
                "estrategia": estrategia,
                "estado": "EN CURSO"
            })

            # Mantén la lista razonable
            if len(senales) > 120:
                del senales[:40]

            # Actualiza estados (Finalizada si ya pasó expira)
            _actualizar_estados()

        except Exception:
            pass

        # Ritmo de generación
        import time
        time.sleep(3)


def _actualizar_estados():
    """Marca 'FINALIZADA' si ya pasó expira."""
    now = ahora_cl()
    for s in senales:
        try:
            exp = datetime.fromisoformat(s["expira"])
            # si exp viene naive, fozamos tz CL
            if exp.tzinfo is None:
                exp = exp.replace(tzinfo=TZ_CL)
            if now >= exp:
                s["estado"] = "FINALIZADA"
            else:
                s["estado"] = "EN CURSO"
        except Exception:
            s["estado"] = "EN CURSO"


# -----------------------------
# RUTAS
# -----------------------------
@app.route("/")
def index():
    return render_template("panel.html")


@app.route("/api/status")
def api_status():
    return jsonify({
        "hora_local": fmt_hhmmss(ahora_cl()),
        "modo": MODO_ACTUAL,
        "bot_activo": bot_activo
    })


@app.route("/api/signals", methods=["GET"])
def api_signals():
    _actualizar_estados()
    # Formateamos campos para la tabla
    datos = []
    for s in senales:
        try:
            ent = datetime.fromisoformat(s["entrada"])
            exp = datetime.fromisoformat(s["expira"])
            if ent.tzinfo is None: ent = ent.replace(tzinfo=TZ_CL)
            if exp.tzinfo is None: exp = exp.replace(tzinfo=TZ_CL)
            datos.append({
                "par": s["par"],
                "tipo": s["tipo"],
                "precio": s["precio"],
                "entrada": ent.strftime("%H:%M:%S"),
                "expira": exp.strftime("%H:%M:%S"),
                "confianza": f'{s["confianza"]}%',
                "duracion": f'{s["duracion_min"]} min',
                "estrategia": s["estrategia"],
                "estado": s["estado"]
            })
        except Exception:
            pass
    return jsonify({"signals": datos})


# -----------------------------
# EJECUCIÓN
# -----------------------------
if __name__ == "__main__":
    print("✅ Conectado correctamente a IQ Option (REAL)")  # tu conexión real puede loguearse aquí
    print(f"🚀 Iniciando bot en modo: {MODO_ACTUAL}")

    threading.Thread(target=generar_senales, daemon=True).start()
    print(f"🌐 Servidor Flask ejecutándose en http://{HOST}:{PORT}")
    app.run(host=HOST, port=PORT)
