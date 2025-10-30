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
from collections import deque

# =======================
#  CONFIG & ESTADO NUEVO
# =======================
CONF_MIN = 85                     # no emitir <85%
COOL_DOWN_MIN = 6                 # no repetir/oponer dentro de esta ventana
MAX_CACHE = 500                   # historial para evitar duplicados
PREAVISO_1M = 30                  # segundos antes para señales de 1m
PREAVISO_3M = 60                  # para 3m
PREAVISO_5M = 90                  # para 5m

# Prioridad de estrategias (la 1 gana si compiten)
PRIORIDADES = [
    "Rechazo de Zona Institucional",
    "Pullback + EMA20",
    "Acción del Precio + Soporte/Resistencia",
    "Ruptura de Nivel + Volumen",
    "Cambio de Tendencia + Confirmación de Vela"
]

# Memorias para control
senales_emitidas = deque(maxlen=MAX_CACHE)           # hashes de señales
bloqueo_por_par = {}                                 # { 'EURUSD': {'sentido': 'CALL/PUT', 'expira': datetime } }

# =========
# UTILIDAD
# =========
def _hash_senal(par, tipo, entrada_dt, expira_dt, dur_min, estrategia):
    return f"{par}|{tipo}|{entrada_dt:%Y%m%d%H%M%S}|{expira_dt:%Y%m%d%H%M%S}|{dur_min}|{estrategia}"

def _to_local_now():
    # usa la hora del sistema donde corre el bot (Render o tu Mac)
    return datetime.now()

def _proximo_open_de_vela():
    """Devuelve el comienzo de la próxima vela M1 (segundos=0)."""
    now = _to_local_now()
    base = now.replace(second=0, microsecond=0)
    return base + timedelta(minutes=1)

def _preaviso_por_duracion(dur_min):
    if dur_min <= 1:
        return PREAVISO_1M
    elif dur_min == 3:
        return PREAVISO_3M
    else:
        return PREAVISO_5M

# ============================
#  CALIBRADOR DE CONFIANZA
# ============================
def calibrar_confianza(raw_conf, confluencias):
    """
    raw_conf: 0-100 que calcule tu lógica actual.
    confluencias: set/list con etiquetas de señales detectadas (ej: ['ema20','zona','volumen','tendencia'])
    Reglas: reducimos “99% falsos” y hacemos 85-95% más honestos.
    """
    conf = max(0, min(100, int(raw_conf)))

    # Bono por confluencia real
    bonus = 0
    if "tendencia" in confluencias: bonus += 3
    if "ema20" in confluencias: bonus += 3
    if "zona" in confluencias: bonus += 4
    if "volumen" in confluencias: bonus += 2
    if "soporte_resistencia" in confluencias: bonus += 2

    conf = min(100, conf + bonus)

    # Penalizaciones: si NO hay zona NI SR, baja el techo (evita 99% “vacíos”)
    if "zona" not in confluencias and "soporte_resistencia" not in confluencias:
        conf = min(conf, 93)

    # Si no hay tendencia alineada con EMA20, limita fuerte
    if "tendencia" not in confluencias or "ema20" not in confluencias:
        conf = min(conf, 91)

    # Normaliza rango útil final
    if conf >= 98:
        conf = 95  # reserva 98-100 solo si algún día agregas validaciones premium
    conf = max(conf, 80)  # evita “79” por redondeos si pasaron filtros

    return conf

# ==========================================
#  RESOLUCIÓN DE CONFLICTOS & PRIORIDADES
# ==========================================
def elegir_mejor_estrategia(candidatas):
    """
    candidatas: lista de dicts con:
      {'par','tipo','duracion_min','estrategia','conf','confluencias', 'precio_actual'}
    Devuelve la mejor según PRIORIDADES y confianza.
    """
    if not candidatas:
        return None
    # Ordena por (prioridad, confianza desc)
    def _key(c):
        prio = PRIORIDADES.index(c['estrategia']) if c['estrategia'] in PRIORIDADES else 999
        return (prio, -c['conf'])
    candidatas_ordenadas = sorted(candidatas, key=_key)
    return candidatas_ordenadas[0]

def ventana_ocupa(bloqueo, ahora):
    """True si hay bloqueo vigente (expira en el futuro)."""
    return bloqueo and bloqueo.get('expira') and bloqueo['expira'] > ahora

# ==================================
#  EMISIÓN + PREAVISO DE LA SEÑAL
# ==================================
def emitir_senal_segura(par, tipo, duracion_min, estrategia, conf, precio_actual):
    """
    - Evita duplicados y opuestos solapados
    - Publica PENDIENTE con preaviso (30/60/90s según duración)
    - Actualiza bloqueo_por_par para impedir contradicción en ventana activa
    """
    ahora = _to_local_now()
    if conf < CONF_MIN:
        return None

    # Chequeo de bloqueo/opuesto
    bloqueo = bloqueo_por_par.get(par)
    if ventana_ocupa(bloqueo, ahora):
        # Si intenta ir en contra del sentido bloqueado, la descartamos
        if bloqueo['sentido'] != tipo:
            return None

    # Tiempos
    open_siguiente = _proximo_open_de_vela()
    preaviso = _preaviso_por_duracion(duracion_min)
    segundos_restantes = (open_siguiente - ahora).total_seconds()

    # Si el preaviso es mayor al tiempo restante, la publicamos ya como PENDIENTE igual
    # y que el usuario alcance la siguiente vela
    if segundos_restantes < preaviso:
        # no hacemos nada extra; simplemente saldrá ya como PENDIENTE
        pass

    entrada_dt = open_siguiente
    expira_dt = entrada_dt + timedelta(minutes=duracion_min)

    # Evita duplicado exacto
    h = _hash_senal(par, tipo, entrada_dt, expira_dt, duracion_min, estrategia)
    if h in senales_emitidas:
        return None

    # Registrar bloqueo del par por toda la ventana (entrada→expira + cooldown)
    bloqueo_por_par[par] = {
        'sentido': tipo,
        'expira': expira_dt + timedelta(minutes=COOL_DOWN_MIN)
    }

    # Calcular confianza calibrada
    # (si ya llega calibrada, pasa igual)
    # conf = calibrar_confianza(conf, confluencias)  # <- si aún no la calibraste antes

    # Publicar al panel con estado "PENDIENTE"
    nueva = {
        'par': par,
        'tipo': tipo,                           # 'CALL' verde / 'PUT' rojo (ya lo tienes)
        'precio': precio_actual,
        'entrada': entrada_dt.strftime("%H:%M:%S"),
        'expira': expira_dt.strftime("%H:%M:%S"),
        'confianza': f"{conf}%",
        'duracion': f"{duracion_min} min",
        'estrategia': estrategia,
        'estado': "PENDIENTE"                   # luego tu bucle la pasa a EN CURSO -> FINALIZADA
    }

    # TODO: integra este dict a tu storage (signals.json o tu lista global) y socket/panel
    # Ejemplo si ya tienes una lista global `senales`:
    try:
        senales.insert(0, nueva)                # al inicio de la tabla
        if len(senales) > 50:
            senales.pop()
    except Exception:
        pass

    # Guarda hash para no duplicar
    senales_emitidas.append(h)
    return nueva
