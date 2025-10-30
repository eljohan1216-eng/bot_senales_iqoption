import threading
from datetime import datetime, timedelta, timezone

try:
    # Python 3.9+ usa zoneinfo por defecto
    from zoneinfo import ZoneInfo
    TZ_CL = ZoneInfo("America/Santiago")
except Exception:
    import pytz
    TZ_CL = pytz.timezone("America/Santiago")

from collections import deque
from flask import Flask, render_template, jsonify

# ==========================================================
# INICIALIZAR APP FLASK
# ==========================================================
app = Flask(__name__)

# ==========================================================
# CONFIGURACIÓN Y ESTADO NUEVO
# ==========================================================
CONF_MIN = 85           # no emitir señales con menos de 85% de confianza
COOL_DOWN_MIN = 6       # evitar señales opuestas en menos de 6 min
MAX_CACHE = 500         # historial para evitar duplicados

# ✅ NUEVO: Enviar señal 1:30 antes (90 segundos)
PREAVISO_1M = 90        # segundos antes para señales de 1 minuto
PREAVISO_3M = 90        # segundos antes para señales de 3 minutos
PREAVISO_5M = 90        # segundos antes para señales de 5 minutos

# Prioridad de estrategias (1 gana si compiten)
PRIORIDADES = [
    "Rechazo de Zona Institucional",
    "Pullback + EMA20",
    "Acción del Precio + Soporte/Resistencia",
    "Ruptura de Nivel + Volumen",
    "Cambio de Tendencia + Confirmación de Vela"
]

# ==========================================================
# MEMORIAS Y CONTROL DE SEÑALES
# ==========================================================
senales_emitidas = deque(maxlen=MAX_CACHE)
bloqueo_por_par = {}  # evitar contradicciones

def _hash_senal(par, tipo, entrada_dt, expira_dt, dur_min, estrategia):
    """Genera un hash único para evitar duplicados."""
    return f"{par}|{tipo}|{entrada_dt:%Y-%m-%d %H:%M:%S}|{expira_dt:%H:%M:%S}|{dur_min}|{estrategia}"

def _to_local_now():
    """Hora local del sistema"""
    return datetime.now(TZ_CL)

def _proximo_cierre_vela():
    """Devuelve el comienzo de la próxima vela M1"""
    base = _to_local_now().replace(second=0, microsecond=0)
    return base + timedelta(minutes=1)

def _preaviso_por_duracion(dur_min):
    # Todas las señales se enviarán 90 segundos antes de la apertura
    return 90

# ==========================================================
# RUTAS DEL PANEL
# ==========================================================
@app.route("/")
def index():
    hora_local = _to_local_now().strftime("%I:%M:%S %p")
    modo_actual = "MIXTO"
    return render_template("panel.html", hora_local=hora_local, modo_actual=modo_actual)

@app.route("/estado")
def estado():
    """Endpoint para el frontend del panel."""
    return jsonify({
        "estado_bot": "Conectado",
        "hora_local": _to_local_now().strftime("%I:%M:%S %p"),
        "modo_actual": "MIXTO"
    })

# ==========================================================
# EJECUCIÓN PRINCIPAL
# ==========================================================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
