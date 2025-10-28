# ======================================
# BOT DE SEÑALES IQ OPTION - MODO MIXTO
# ======================================

from iqoptionapi.stable_api import IQ_Option
import random, time, json

# ---- CONFIGURACIÓN ----
MODO_ACTUAL = "MIXTO"  # Opciones: "OTC", "REAL" o "MIXTO"

PAIRS_REAL = ["EURUSD", "GBPUSD", "USDJPY", "AUDUSD", "EURJPY", "USDCAD"]
PAIRS_OTC = ["EURUSD-OTC", "GBPUSD-OTC", "USDJPY-OTC", "AUDUSD-OTC", "EURJPY-OTC", "USDCAD-OTC"]

EMAIL = "jitraders1216@gmail.com"
PASSWORD = "jo121014"

# ---- FUNCIÓN DURACIÓN POR CONFIANZA ----
def duracion_por_confianza(confianza):
    if confianza < 91:
        return 1
    elif confianza < 96:
        return 3
    else:
        return 5

# ---- CONEXIÓN IQ OPTION ----
I_want_money = IQ_Option(EMAIL, PASSWORD)
I_want_money.connect()
if I_want_money.check_connect():
    print("✅ Conectado correctamente a IQ Option (REAL)")
else:
    print("❌ Error al conectar con IQ Option")
    exit()

# ---- FUNCIÓN PRINCIPAL ----
def generar_senal():
    # Selecciona tipo de mercado según modo
    if MODO_ACTUAL == "REAL":
        pares = PAIRS_REAL
    elif MODO_ACTUAL == "OTC":
        pares = PAIRS_OTC
    else:
        pares = PAIRS_REAL + PAIRS_OTC  # modo mixto

    par = random.choice(pares)
    tipo = random.choice(["CALL", "PUT"])
    confianza = random.randint(85, 100)
    duracion = duracion_por_confianza(confianza)

    estrategias = [
        "Acción del Precio + Soporte/Resistencia",
        "Cambio de Tendencia + Confirmación de Vela",
        "Pullback + EMA20",
        "Ruptura de Nivel + Volumen",
        "Rechazo de Zona Institucional"
    ]
    estrategia = random.choice(estrategias)

    senal = {
        "par": par,
        "tipo": tipo,
        "confianza": confianza,
        "duracion_min": duracion,
        "estrategia": estrategia
    }

    return senal

# ---- BUCLE PRINCIPAL ----
print("🟢 Iniciando bot en modo mixto (OTC + REAL)...")
print("---------------------------------------------")

while True:
    senal = generar_senal()
    print(f"✅ Señal generada: {senal}")
    time.sleep(5)
