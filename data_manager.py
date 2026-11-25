"""
Bingo Poker Club 2026 — capa de datos sobre Supabase.
Credenciales en .streamlit/secrets.toml (o en Secrets de Streamlit Cloud):

    SUPABASE_URL = "https://xxxx.supabase.co"
    SUPABASE_KEY = "<service_role key>"
    ADMIN_PASSWORD = "<clave admin>"
"""
import pandas as pd
import requests
import streamlit as st

POINTS_RULES = {
    "Torneo Regular Shorthanded (SH)": {1: 30, 2: 10, 3: 0, 4: 0, 5: 0},
    "Torneo Regular Full ring (FR)": {1: 50, 2: 35, 3: 20, 4: 10, 5: 0},
    "Torneo Regular Multitable (MM)": {1: 70, 2: 50, 3: 30, 4: 20, 5: 0},
    "Main Event Shorthanded (SH)": {1: 70, 2: 30, 3: 0, 4: 0, 5: 0},
    "Main Event Full ring (FR)": {1: 100, 2: 75, 3: 40, 4: 20, 5: 10},
    "Main Event Multitable (MM)": {1: 130, 2: 90, 3: 50, 4: 35, 5: 20},
}

FECHAS_STANDARD = [f"{i:02d}" for i in range(1, 11)]
DEFAULT_EVENTO_FINAL = "Sábado 16 de enero 2027 desde las 14 horas"


# ─── Cliente REST mínimo ─────────────────────────────────────────────────────
def _cfg():
    try:
        return st.secrets["SUPABASE_URL"].rstrip("/"), st.secrets["SUPABASE_KEY"]
    except Exception:
        raise RuntimeError("Faltan SUPABASE_URL / SUPABASE_KEY en los Secrets de Streamlit.")

def _headers(extra=None):
    _, key = _cfg()
    h = {"apikey": key, "Content-Type": "application/json"}
    if key.startswith("eyJ"):  # key antigua (JWT service_role); las nuevas sb_secret_ van solo en apikey
        h["Authorization"] = f"Bearer {key}"
    if extra:
        h.update(extra)
    return h

def _get(table, query="select=*"):
    url, _ = _cfg()
    r = requests.get(f"{url}/rest/v1/{table}?{query}", headers=_headers(), timeout=15)
    if r.status_code >= 300:
        raise RuntimeError(f"Supabase {r.status_code} leyendo {table}: {r.text[:300]}")
    return r.json()

def _rpc(fn, params):
    url, _ = _cfg()
    r = requests.post(f"{url}/rest/v1/rpc/{fn}", headers=_headers(), json=params, timeout=20)
    if r.status_code >= 300:
        raise RuntimeError(f"Supabase {r.status_code}: {r.text[:300]}")

def _insert(table, rows):
    url, _ = _cfg()
    r = requests.post(f"{url}/rest/v1/{table}", headers=_headers({"Prefer": "return=minimal"}), json=rows, timeout=15)
    if r.status_code >= 300:
        raise RuntimeError(f"Supabase {r.status_code}: {r.text[:300]}")


# ─── Lectura ─────────────────────────────────────────────────────────────────
def _payouts(total_rake):
    camp, mf = total_rake * 0.50, total_rake * 0.40
    return [
        {"Pos": 1, "Campeonato": int(camp * 0.50), "Mesa Final": int(mf * 0.50)},
        {"Pos": 2, "Campeonato": int(camp * 0.30), "Mesa Final": int(mf * 0.30)},
        {"Pos": 3, "Campeonato": int(camp * 0.20), "Mesa Final": int(mf * 0.20)},
    ]

def load_data():
    jugadores = _get("bpc_jugadores", "select=id,nombre&activo=eq.true&order=id")
    resultados = _get("bpc_resultados", "select=fecha,jugador_id,puntos")
    fechas = _get("bpc_fechas", "select=fecha,tipo_torneo,sub_code,rake")
    calendario = _get("bpc_calendario", "select=*&order=orden")

    # Posiciones (mismo formato que antes: Pos, Jugador, 01..10, Total)
    pts_by = {(r["jugador_id"], r["fecha"]): int(r["puntos"] or 0) for r in resultados}
    rows = []
    for j in jugadores:
        pts = {f: pts_by.get((j["id"], i + 1), 0) for i, f in enumerate(FECHAS_STANDARD)}
        rows.append({"Pos": 0, "Jugador": j["nombre"], **pts, "Total": sum(pts.values())})
    df_pos = pd.DataFrame(rows, columns=["Pos", "Jugador"] + FECHAS_STANDARD + ["Total"])
    if not df_pos.empty:
        df_pos = df_pos.sort_values(by=["Total", "Jugador"], ascending=[False, True]).reset_index(drop=True)
        df_pos["Pos"] = range(1, len(df_pos) + 1)

    # Rake y subheaders
    f_map = {f["fecha"]: f for f in fechas}
    rake_dict = {f"F{i}": float(f_map.get(i, {}).get("rake") or 0) for i in range(1, 11)}
    subheaders = [(f_map.get(i, {}).get("sub_code") or "") for i in range(1, 11)]
    total_rake = sum(rake_dict.values())

    # Estado de cada fecha (registrada = tiene resultados o fila en bpc_fechas)
    con_puntos = {r["fecha"] for r in resultados if (r["puntos"] or 0) > 0}
    fechas_info = {}
    for i in range(1, 11):
        f = f_map.get(i, {})
        fechas_info[i] = {
            "registrada": (i in f_map) or (i in con_puntos),
            "tipo": f.get("tipo_torneo"),
            "sub": f.get("sub_code") or "",
            "rake": float(f.get("rake") or 0),
        }

    # Calendario: "próximo" = primera fecha que aún no tiene resultados
    jugadas = {r["fecha"] for r in resultados if (r["puntos"] or 0) > 0}
    ultima = max(jugadas) if jugadas else 0
    schedule_data, evento_final, marcado = [], DEFAULT_EVENTO_FINAL, False
    for c in calendario:
        if c.get("es_final"):
            evento_final = c["descripcion"]
            continue
        if c.get("fecha_num") and c["fecha_num"] <= ultima:
            continue  # ya se jugó, no se muestra
        schedule_data.append({
            "fecha": f"Fecha {c['fecha_num']}" if c.get("fecha_num") else "",
            "mes": c.get("mes") or "",
            "desc": c["descripcion"],
            "next": not marcado,
        })
        marcado = True

    return {
        "df_posiciones": df_pos,
        "fechas_headers": FECHAS_STANDARD,
        "subheaders": subheaders,
        "rake_dict": rake_dict,
        "total_rake": total_rake,
        "camp_total": total_rake * 0.50,
        "mf_total": total_rake * 0.40,
        "gastos_mf": total_rake * 0.10,
        "payouts": _payouts(total_rake),
        "schedule_data": schedule_data,
        "evento_final": evento_final,
        "fechas_info": fechas_info,
    }


# ─── Escritura ───────────────────────────────────────────────────────────────
def save_fecha(fecha_num, tipo_torneo, sub_code, rake, resultados):
    """Guarda UNA fecha (atómico). resultados = [{"jugador": nombre, "puntos": n}, ...]"""
    try:
        _rpc("bpc_guardar_fecha", {
            "p_fecha": int(fecha_num),
            "p_tipo": tipo_torneo,
            "p_sub": sub_code,
            "p_rake": float(rake or 0),
            "p_resultados": resultados,
        })
        return True, None
    except Exception as e:
        return False, str(e)

def add_player(nombre):
    try:
        _insert("bpc_jugadores", [{"nombre": nombre}])
        return True, None
    except Exception as e:
        return False, str(e)

def _delete(table, query):
    url, _ = _cfg()
    r = requests.delete(f"{url}/rest/v1/{table}?{query}", headers=_headers(), timeout=15)
    if r.status_code >= 300:
        raise RuntimeError(f"Supabase {r.status_code}: {r.text[:300]}")

def delete_fecha(fecha_num):
    """Borra resultados y rake de una fecha (vuelve a quedar pendiente)."""
    try:
        _delete("bpc_resultados", f"fecha=eq.{int(fecha_num)}")
        _delete("bpc_fechas", f"fecha=eq.{int(fecha_num)}")
        return True, None
    except Exception as e:
        return False, str(e)

def update_evento_final(texto):
    """Cambia la fecha/hora del Gran Evento Mesa Final."""
    if not texto:
        return False, "El texto no puede quedar vacío."
    try:
        url, _ = _cfg()
        h = _headers({"Prefer": "return=representation"})
        r = requests.patch(f"{url}/rest/v1/bpc_calendario?es_final=eq.true", headers=h, json={"descripcion": texto}, timeout=15)
        if r.status_code >= 300:
            raise RuntimeError(f"Supabase {r.status_code}: {r.text[:300]}")
        if not r.json():  # no existía la fila → crearla
            _insert("bpc_calendario", [{"orden": 99, "descripcion": texto, "es_final": True}])
        return True, None
    except Exception as e:
        return False, str(e)
