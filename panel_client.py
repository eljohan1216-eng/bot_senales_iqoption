# panel_client.py
import json, requests, os

def _cfg():
    """Lee configuración desde config.json"""
    with open("config.json", "r") as f:
        return json.load(f)

def _headers(cfg):
    """Encabezados con token de seguridad"""
    return {"Authorization": f"Bearer {cfg['PANEL_TOKEN']}"}

def push_signals(signals):
    """
    Envía señales al panel web.
    Ejemplo de señales:
    [{"par": "EURUSD", "tipo": "CALL", "hora": "13:02", "confianza": 92, "duracion_min": 3}]
    """
    cfg = _cfg()
    url = cfg["PANEL_URL"].rstrip("/") + "/api/signals"
    r = requests.post(url, json=signals, headers=_headers(cfg), timeout=40)
    r.raise_for_status()
    print("✅ Señales enviadas al panel correctamente.")
    return r.json()

def set_mode(mode_str):
    """Cambia el modo del panel entre OTC o REAL"""
    cfg = _cfg()
    url = cfg["PANEL_URL"].rstrip("/") + "/api/mode"
    r = requests.post(url, json={"modo": mode_str}, headers=_headers(cfg), timeout=40)
    r.raise_for_status()
    print(f"🔁 Modo actualizado en el panel: {mode_str}")
    return r.json()

def set_active(active: bool):
    """Activa o desactiva el bot desde el panel"""
    cfg = _cfg()
    url = cfg["PANEL_URL"].rstrip("/") + "/api/toggle-bot"
    r = requests.post(url, json={"force": True, "activo": active}, headers=_headers(cfg), timeout=40)
    r.raise_for_status()
    estado = "ACTIVO" if active else "DETENIDO"
    print(f"⚙️ Estado del bot cambiado a: {estado}")
    return r.json()
