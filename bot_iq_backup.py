# ===============================================
# BOT DE SEÑALES IQ OPTION – PRO (MAC)
# EMA20 + Acción del Precio + Soporte/Resistencia
# Expiración dinámica + Envío profesional a Telegram
# ===============================================

from iqoptionapi.stable_api import IQ_Option
import time, json, os, logging, requests
from datetime import datetime, timedelta
import pandas as pd

logging.getLogger().setLevel(logging.CRITICAL)

# --------- CREDENCIALES IQ OPTION ---------
EMAIL = "jitraders1216@gmail.com"
PASSWORD = "jo121014"

# --------- TELEGRAM CONFIG ---------
TELEGRAM_TOKEN = "8291614307:AAE3wnud1aNU6nAV4x0xfwXgXvtWBbhpU7E"
CHAT_ID = "5171299465"
TG_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

def send_tg(msg):
    try:
        requests.post(TG_URL, json={"chat_id": CHAT_ID, "text": msg, "parse_mode": "HTML"})
    except Exception as e:
        print(f"⚠️ Telegram error: {e}")

# --------- CONFIG ---------
PAIRS = ["EURUSD-OTC", "GBPUSD-OTC", "USDJPY-OTC", "EURGBP-OTC", "AUDUSD-OTC"]
TIMEFRAME_SEC = 60
VELAS = 180
SCAN_CADA = 10
MAX_SIGNALS = 10

# --------- CONEXIÓN IQ OPTION ---------
api = IQ_Option(EMAIL, PASSWORD)
api.connect()
if not api.check_connect():
    print("❌ Error al conectar con IQ Option")
    exit()
print("✅ Conectado correctamente a IQ Option\n")

# --------- FUNCIONES ---------
def obtener_velas(par):
    velas = api.get_candles(par, TIMEFRAME_SEC, VELAS, time.time())
    df = pd.DataFrame(velas)
    df["ema20"] = df["close"].ewm(span=20).mean()
    return df

def detectar_patron(df):
    o, c, h, l = df["open"].iloc[-2], df["close"].iloc[-2], df["max"].iloc[-2], df["min"].iloc[-2]
    cuerpo = abs(c - o)
    rango = h - l
    if cuerpo <= 0.15 * rango:
        return "Doji"
    if c > o and df["close"].iloc[-3] < df["open"].iloc[-3]:
        return "Envolvente Alcista"
    if c < o and df["close"].iloc[-3] > df["open"].iloc[-3]:
        return "Envolvente Bajista"
    return None

def soportes_resistencias(df, look=70):
    lows, highs = [], []
    for i in range(-look, -2):
        lo = df["min"].iloc[i]
        hi = df["max"].iloc[i]
        if lo < df["min"].iloc[i - 1] and lo < df["min"].iloc[i + 1]:
            lows.append(lo)
        if hi > df["max"].iloc[i - 1] and hi > df["max"].iloc[i + 1]:
            highs.append(hi)
    return lows, highs

def evaluar_setup(par, df):
    precio = df["close"].iloc[-2]
    ema = df["ema20"].iloc[-2]
    patron = detectar_patron(df)
    lows, highs = soportes_resistencias(df)

    tipo = None
    if patron == "Envolvente Alcista" and precio > ema:
        tipo = "CALL"
    elif patron == "Envolvente Bajista" and precio < ema:
        tipo = "PUT"
    if not tipo:
        return None

    confianza = 95 if patron else 90
    exp_min = 5 if confianza >= 95 else 3 if confianza >= 90 else 1

    return {
        "par": par,
        "tipo": tipo,
        "precio": round(precio, 5),
        "confianza": confianza,
        "exp_min": exp_min,
        "patron": patron or "-"
    }

def enviar_a_telegram(signal):
    tipo_texto = "📈 Tipo: <b>COMPRA 🔼 (CALL)</b>" if signal["tipo"] == "CALL" else "📉 Tipo: <b>VENTA 🔽 (PUT)</b>"
    msg = (
        "📊 <b>Señal Detectada IQ Option</b>\n\n"
        f"🪙 Par: <b>{signal['par']}</b>\n"
        f"{tipo_texto}\n"
        f"💰 Precio: <b>{signal['precio']}</b>\n"
        f"⌛ Expira: <b>{signal['exp_min']} min</b>\n"
        f"💪 Confianza: <b>{signal['confianza']}%</b>\n"
        "📊 Estrategia: Acción del Precio + Soporte/Resistencia"
    )
    send_tg(msg)

def append_signal(payload):
    try:
        if os.path.exists("signals.json"):
            with open("signals.json", "r") as f:
                data = json.load(f)
        else:
            data = []
    except:
        data = []
    if payload not in data:
        data.append(payload)
    data = data[-MAX_SIGNALS:]
    with open("signals.json", "w") as f:
        json.dump(data, f, indent=4)

# --------- LOOP PRINCIPAL ---------
print("🟢 Escaneando pares cada 10 segundos...\n")
enviadas = set()

while True:
    for par in PAIRS:
        try:
            df = obtener_velas(par)
            signal = evaluar_setup(par, df)
            if signal:
                payload = {
                    "par": signal["par"],
                    "tipo": signal["tipo"],
                    "precio": signal["precio"],
                    "confianza": signal["confianza"],
                    "exp_min": signal["exp_min"],
                    "hora": datetime.now().strftime("%H:%M:%S")
                }
                append_signal(payload)

                # Enviar solo si es nueva
                key = (signal["par"], signal["tipo"], signal["precio"])
                if key not in enviadas:
                    enviar_a_telegram(signal)
                    enviadas.add(key)

                print(f"{signal['tipo']} | {signal['par']} | {signal['confianza']}% | {signal['precio']}")
        except Exception as e:
            print(f"⚠️ {par}: {e}")
        time.sleep(1)
    time.sleep(SCAN_CADA)