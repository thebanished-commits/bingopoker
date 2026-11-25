import os
import base64
import html
import streamlit as st
import data_manager
import report_generator

st.set_page_config(
    page_title="Bingo Poker Club 2026",
    page_icon="🏆",
    layout="wide",
    initial_sidebar_state="collapsed",
)

N_FECHAS = 10
NA = "— Seleccionar —"
ADMIN_PASSWORD = st.secrets.get("ADMIN_PASSWORD", "")


def fmt_money(val):
    try:
        return f"${int(round(val)):,}".replace(",", ".")
    except Exception:
        return "$0"


def esc(x):
    return html.escape(str(x))


def medal(pos, size=""):
    """Medalla con número grande y legible (reemplaza los emojis)."""
    cls = {1: "mg", 2: "ms", 3: "mb"}.get(pos, "mn")
    return f'<span class="md {cls} {size}">{pos}</span>'


@st.cache_data
def get_logo_b64():
    base = os.path.dirname(__file__)
    for name in ("logo_small.png", "logo.png"):
        p = os.path.join(base, "assets", name)
        if os.path.exists(p):
            with open(p, "rb") as f:
                return base64.b64encode(f.read()).decode()
    return None


logo_b64 = get_logo_b64()
st.session_state.setdefault("is_admin", False)

# ─── ESTILOS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@600;700;800&family=Plus+Jakarta+Sans:wght@500;600;700;800&display=swap');

:root { --gold:#f59e0b; --gold2:#facc15; --ink:#f1f5f9; --muted:#94a3b8; --line:rgba(245,158,11,.22);
        --card:linear-gradient(160deg, rgba(30,41,59,.85), rgba(15,23,42,.92)); }
.stApp { background: radial-gradient(1200px 600px at 50% -10%, #23205a 0%, #0f172a 45%, #070b14 100%) !important;
         font-family:'Plus Jakarta Sans', sans-serif; }
.block-container { padding-top: 4.2rem !important; max-width: 1180px; }
h1,h2,h3 { font-family:'Outfit', sans-serif !important; letter-spacing:.3px; }
.sec-title { font-family:'Outfit',sans-serif; font-size:1.35rem; font-weight:800; color:var(--ink); margin:.4rem 0 .1rem; }
.sec-cap { color:var(--muted); font-size:.88rem; margin-bottom:.8rem; }

/* Header */
.hdr { display:flex; align-items:center; gap:18px; padding:14px 22px; margin-bottom:16px;
       background:linear-gradient(90deg, rgba(49,46,129,.55), rgba(15,23,42,.6)); border:1px solid rgba(245,158,11,.45);
       border-radius:18px; box-shadow:0 10px 30px rgba(0,0,0,.35); }
.hdr-logo { width:84px; height:84px; border-radius:50%; object-fit:cover; flex-shrink:0;
            box-shadow:0 0 0 2px var(--gold), 0 0 24px rgba(245,158,11,.35); }
.hdr-title { font-family:'Outfit',sans-serif; font-weight:800; font-size:2rem; line-height:1.05;
             background:linear-gradient(135deg,#fffbeb,#facc15 45%,#f59e0b); -webkit-background-clip:text; -webkit-text-fill-color:transparent; }
.hdr-sub { color:#cbd5e1; font-size:.8rem; font-weight:700; letter-spacing:1.6px; text-transform:uppercase; margin-top:5px; }
.hdr-next { margin-left:auto; text-align:right; padding-left:18px; border-left:1px solid var(--line); }
.hdr-next small { display:block; color:var(--muted); font-size:.7rem; font-weight:800; letter-spacing:1.2px; text-transform:uppercase; }
.hdr-next b { color:var(--gold2); font-size:1.05rem; font-weight:800; }
.hdr-next span { display:block; color:#e2e8f0; font-size:.85rem; font-weight:600; }

/* Podio */
.podium { display:grid; grid-template-columns:1fr 1.15fr 1fr; gap:14px; align-items:end; margin:6px 0 0; }
.pod { background:var(--card); border:1px solid var(--line); border-radius:16px; padding:14px 12px; text-align:center;
       box-shadow:0 8px 22px rgba(0,0,0,.35); }
.pod .m { line-height:1; }
.pod .n { font-family:'Outfit',sans-serif; font-weight:800; font-size:1.2rem; color:var(--ink); margin-top:6px; }
.pod .p { font-family:'Outfit',sans-serif; font-weight:800; font-size:1.55rem; color:var(--gold2); }
.pod .g { color:var(--muted); font-size:.78rem; font-weight:700; }
.pod.first { border:2px solid var(--gold); padding:22px 12px; background:linear-gradient(160deg, rgba(180,83,9,.35), rgba(15,23,42,.95));
             box-shadow:0 0 28px rgba(245,158,11,.28); }
.pod.first .n { font-size:1.4rem; } .pod.first .p { font-size:1.9rem; }

/* Medallas */
.md { display:inline-flex; align-items:center; justify-content:center; width:30px; height:30px; border-radius:50%;
      font-family:'Outfit',sans-serif; font-weight:800; font-size:1rem; color:#111827; flex-shrink:0;
      box-shadow:inset 0 -2px 0 rgba(0,0,0,.25), 0 2px 6px rgba(0,0,0,.35); }
.md.mg { background:linear-gradient(145deg,#fde68a,#f59e0b); }
.md.ms { background:linear-gradient(145deg,#f1f5f9,#94a3b8); }
.md.mb { background:linear-gradient(145deg,#fdba74,#b45309); }
.md.mn { background:transparent; color:var(--muted); box-shadow:none; }
.md.lg { width:46px; height:46px; font-size:1.45rem; }
.md.xl { width:58px; height:58px; font-size:1.85rem; }

/* Bloque de pozos */
.money { display:grid; grid-template-columns:1.25fr 1fr 1fr; gap:12px; margin:26px 0 8px; }
.mtot { border-radius:16px; padding:16px 20px; background:linear-gradient(135deg,#fbbf24,#d97706); color:#111827;
        box-shadow:0 8px 26px rgba(245,158,11,.3); }
.mtot small { display:block; font-size:.75rem; font-weight:800; letter-spacing:1px; text-transform:uppercase; opacity:.8; }
.mtot b { display:block; font-family:'Outfit',sans-serif; font-size:2.3rem; font-weight:800; line-height:1.1; }
.mtot span { font-size:.82rem; font-weight:700; opacity:.8; }
.mcard { border-radius:16px; padding:16px 18px; background:var(--card); border:1px solid rgba(245,158,11,.4); }
.mcard small { display:block; color:var(--ink); font-size:.95rem; font-weight:800; }
.mcard em { display:block; font-style:normal; color:var(--muted); font-size:.75rem; font-weight:700; margin-bottom:4px; }
.mcard b { font-family:'Outfit',sans-serif; font-size:1.9rem; font-weight:800; color:var(--gold2); }
.morg { text-align:right; color:var(--muted); font-size:.8rem; font-weight:700; margin-bottom:12px; }
.morg b { color:#cbd5e1; }

/* Franja de pozos */
.strip { display:grid; grid-template-columns:repeat(4,1fr); background:var(--card); border:1px solid var(--line);
         border-radius:16px; margin-bottom:10px; overflow:hidden; }
.strip > div { padding:12px 16px; border-right:1px solid var(--line); }
.strip > div:last-child { border-right:none; }
.strip small { display:block; color:var(--muted); font-size:.72rem; font-weight:800; letter-spacing:.8px; text-transform:uppercase; }
.strip b { font-family:'Outfit',sans-serif; font-size:1.35rem; font-weight:800; color:var(--ink); }
.strip .hl b { color:var(--gold2); }

/* Tabs */
.stTabs [role="tablist"], .stTabs [data-baseweb="tab-list"] { gap:8px !important; border-bottom:1px solid var(--line) !important; padding-bottom:10px !important; flex-wrap:wrap; }
.stTabs [role="tab"] { padding:8px 18px !important; border-radius:999px !important; border:1px solid rgba(245,158,11,.35) !important;
       background:rgba(15,23,42,.7) !important; color:#e2e8f0 !important; font-weight:700 !important; height:auto !important; }
.stTabs [role="tab"] p { font-size:.95rem !important; font-weight:700 !important; color:#e2e8f0 !important; }
.stTabs [role="tab"][aria-selected="true"] { background:linear-gradient(135deg,#f59e0b,#d97706) !important; border-color:#fde68a !important; }
.stTabs [role="tab"][aria-selected="true"] p { color:#111827 !important; }
.stTabs [role="tab"]::after, .stTabs [role="tab"]::before { display:none !important; }
.stTabs [data-baseweb="tab-highlight"], .stTabs [data-baseweb="tab-border"], .stTabs .react-aria-SelectionIndicator { display:none !important; }

/* Botones */
.stButton>button, .stDownloadButton>button, .stFormSubmitButton>button {
  background:linear-gradient(135deg,#f59e0b,#d97706) !important; color:#111827 !important; font-weight:800 !important;
  border:none !important; border-radius:12px !important; box-shadow:0 4px 14px rgba(245,158,11,.3) !important; }
.stButton>button:disabled { background:#334155 !important; color:#94a3b8 !important; box-shadow:none !important; }
.stButton>button[kind="secondary"].ghost { background:transparent !important; }

/* Tabla posiciones (escritorio) */
.lb { width:100%; border-collapse:separate; border-spacing:0 6px; }
.lb th { color:var(--gold2); font-size:.78rem; font-weight:800; text-transform:uppercase; letter-spacing:.6px; padding:6px 8px; text-align:center; }
.lb th small { display:block; color:var(--muted); font-size:.65rem; font-weight:700; }
.lb th.l, .lb td.l { text-align:left; }
.lb td { background:rgba(30,41,59,.7); padding:11px 8px; text-align:center; color:var(--ink); font-weight:700; font-size:.95rem;
         border-top:1px solid rgba(245,158,11,.12); border-bottom:1px solid rgba(245,158,11,.12); }
.lb td:first-child { border-left:1px solid rgba(245,158,11,.12); border-radius:12px 0 0 12px; width:48px; color:var(--muted); }
.lb td:last-child { border-right:1px solid rgba(245,158,11,.12); border-radius:0 12px 12px 0; font-family:'Outfit',sans-serif;
                    font-size:1.15rem; color:var(--gold2); font-weight:800; }
.lb tr.r1 td { background:rgba(180,83,9,.28); border-color:rgba(245,158,11,.6); }
.lb tr.r2 td { background:rgba(100,116,139,.25); }
.lb tr.r3 td { background:rgba(146,64,14,.2); }
.lb td.z { color:#334155; }
.lb td.pt { color:#4ade80; }
.lb td.last { box-shadow: inset 0 0 0 999px rgba(250,204,21,.05); }

/* Tarjetas posiciones (celular) */
.lbm { display:none; }
.lbx-wrap { display:none; }
.lbm details { background:rgba(30,41,59,.75); border:1px solid rgba(245,158,11,.15); border-radius:12px; margin-bottom:8px; }
.lbm details.r1 { border-color:var(--gold); background:rgba(180,83,9,.25); }
.lbm summary { list-style:none; display:flex; align-items:center; gap:10px; padding:12px 14px; cursor:pointer; }
.lbm summary::-webkit-details-marker { display:none; }
.lbm .pos { width:28px; color:var(--muted); font-weight:800; text-align:center; }
.lbm .nm { flex:1; color:var(--ink); font-weight:800; }
.lbm .lf { color:#4ade80; font-size:.78rem; font-weight:800; }
.lbm .tt { font-family:'Outfit',sans-serif; color:var(--gold2); font-weight:800; font-size:1.15rem; min-width:64px; text-align:right; }
.lbm .det { display:flex; flex-wrap:wrap; gap:6px; padding:0 14px 12px 52px; }
.lbm .det span { background:rgba(15,23,42,.8); border:1px solid rgba(148,163,184,.2); border-radius:8px; padding:3px 8px; font-size:.78rem; color:#cbd5e1; font-weight:700; }
.lbm .det span b { color:#4ade80; }

/* Pozos */
.prizes { display:grid; grid-template-columns:repeat(3,1fr); gap:14px; margin:6px 0 18px; }
.prize { background:var(--card); border:1px solid var(--line); border-radius:16px; padding:16px; }
.prize h4 { color:var(--gold2); font-size:.82rem; font-weight:800; letter-spacing:.8px; text-transform:uppercase; margin:0 0 2px; }
.prize .tot { font-family:'Outfit',sans-serif; font-size:1.6rem; font-weight:800; color:var(--ink); padding-bottom:8px; border-bottom:1px solid var(--line); margin-bottom:6px; }
.prize .row { display:flex; justify-content:space-between; padding:5px 0; color:#cbd5e1; font-weight:600; font-size:.93rem; }
.prize .row b { color:var(--gold2); font-family:'Outfit',sans-serif; font-size:1.1rem; }
.prize .row { align-items:center; } .prize .pl { display:flex; align-items:center; gap:10px; }
.rakes { display:grid; grid-template-columns:repeat(5,1fr); gap:10px; }
.rk { background:var(--card); border:1px solid rgba(148,163,184,.18); border-radius:12px; padding:10px; text-align:center; }
.rk small { color:var(--muted); font-size:.72rem; font-weight:800; text-transform:uppercase; }
.rk b { display:block; font-family:'Outfit',sans-serif; font-size:1.15rem; color:var(--ink); }
.rk.ok { border-color:rgba(34,197,94,.55); } .rk.ok b { color:var(--gold2); }
.rk.pend b { color:#475569; }

/* Calendario */
.cal { display:flex; align-items:center; justify-content:space-between; gap:12px; background:var(--card); border:1px solid var(--line);
       border-radius:14px; padding:14px 18px; margin-bottom:10px; }
.cal .f { font-family:'Outfit',sans-serif; font-weight:800; color:var(--gold2); font-size:1.15rem; min-width:90px; }
.cal .d { color:var(--ink); font-weight:700; }
.cal.next { border:2px solid var(--gold); box-shadow:0 0 20px rgba(245,158,11,.25); }
.badge { background:var(--gold); color:#111827; font-weight:800; font-size:.7rem; padding:3px 9px; border-radius:999px; text-transform:uppercase; margin-left:8px; }
.final { text-align:center; padding:20px; border-radius:16px; border:2px solid var(--gold2); margin-top:16px;
         background:linear-gradient(135deg,#1e1b4b,rgba(180,83,9,.4)); }
.final h3 { color:var(--gold2) !important; margin:0 0 4px; }
.final div { color:#fff; font-weight:700; font-size:1.1rem; }

/* Admin */
.state { border-radius:12px; padding:12px 14px; margin:4px 0 10px; font-weight:600; font-size:.92rem; }
.state.ok { background:rgba(34,197,94,.1); border:1px solid rgba(34,197,94,.45); color:#bbf7d0; }
.state.pend { background:rgba(245,158,11,.08); border:1px solid rgba(245,158,11,.4); color:#fde68a; }
.chips { display:flex; flex-wrap:wrap; gap:6px; margin-top:6px; }
.chips span { background:rgba(15,23,42,.8); border:1px solid rgba(148,163,184,.25); border-radius:999px; padding:3px 10px; font-size:.82rem; color:#e2e8f0; }
.chips span b { color:#4ade80; }
.summary { background:var(--card); border:1px dashed rgba(245,158,11,.5); border-radius:14px; padding:12px 14px; margin:8px 0; }
.summary h5 { margin:0 0 4px; color:var(--gold2); font-size:.8rem; text-transform:uppercase; letter-spacing:.8px; }

.empty { text-align:center; padding:28px; border:1px dashed rgba(245,158,11,.3); border-radius:14px; color:var(--muted); font-weight:600; }
.foot { text-align:center; margin-top:2.5rem; padding:1rem; border-top:1px solid var(--line); color:#64748b; font-size:.8rem; font-weight:600; }
.foot b { color:var(--gold); }

@media (max-width: 760px) {
  .block-container { padding-top: 3.6rem !important; padding-left:.8rem !important; padding-right:.8rem !important; }
  .hdr { gap:12px; padding:10px 12px; flex-wrap:wrap; }
  .hdr-logo { width:58px; height:58px; }
  .hdr-title { font-size:1.3rem; } .hdr-sub { font-size:.66rem; letter-spacing:1px; }
  .hdr-next { margin-left:0; width:100%; text-align:left; border-left:none; border-top:1px solid var(--line); padding:8px 0 0; }
  .hdr-next b, .hdr-next span { display:inline; } .hdr-next span::before { content:" · "; color:var(--muted); }
  .podium { gap:8px; } .pod { padding:10px 6px; } .pod.first { padding:14px 6px; }
  .pod .n { font-size:.95rem; } .pod.first .n { font-size:1.05rem; } .pod .p { font-size:1.15rem; } .pod.first .p { font-size:1.4rem; }
  .strip { grid-template-columns:repeat(2,1fr); }
  .strip > div:nth-child(2) { border-right:none; } .strip > div:nth-child(-n+2) { border-bottom:1px solid var(--line); }
  .strip b { font-size:1.1rem; }
  .lb { display:none !important; } .lbm { display:block !important; }
  .lbx-wrap { display:block; margin-top:6px; }
  .lbx-wrap > summary { list-style:none; cursor:pointer; text-align:center; padding:11px; border-radius:12px; font-weight:800;
       color:var(--gold2); border:1px solid rgba(245,158,11,.5); background:rgba(15,23,42,.7); }
  .lbx-wrap > summary::-webkit-details-marker { display:none; }
  .lbx-wrap[open] > summary { margin-bottom:8px; }
  .lbx-scroll { overflow-x:auto; -webkit-overflow-scrolling:touch; border-radius:12px; }
  .lb.lbx { display:table !important; min-width:560px; border-spacing:0 4px; }
  .lb.lbx td, .lb.lbx th { padding:9px 7px; font-size:.85rem; }
  .lb.lbx td:nth-child(2), .lb.lbx th:nth-child(2) { position:sticky; left:0; z-index:1; background:#141b2e; }
  .lb.lbx tr.r1 td:nth-child(2) { background:#3a2614; }
  .md { width:26px; height:26px; font-size:.9rem; } .md.lg { width:36px; height:36px; font-size:1.15rem; } .md.xl { width:44px; height:44px; font-size:1.4rem; }
  .money { grid-template-columns:1fr 1fr; gap:10px; margin-top:20px; }
  .mtot { grid-column:1 / -1; padding:14px 16px; } .mtot b { font-size:1.9rem; }
  .mcard { padding:12px 14px; } .mcard small { font-size:.85rem; } .mcard b { font-size:1.35rem; }
  .morg { text-align:center; }
  .prizes { grid-template-columns:1fr; } .rakes { grid-template-columns:repeat(2,1fr); }
  .cal { flex-direction:column; align-items:flex-start; gap:4px; }
  .stTabs [role="tab"] { padding:6px 12px !important; } .stTabs [role="tab"] p { font-size:.85rem !important; }
}
</style>
""", unsafe_allow_html=True)

# ─── ADMIN (sidebar) ─────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### Acceso administrador")
    if not st.session_state["is_admin"]:
        pwd = st.text_input("Clave de administrador", type="password")
        if st.button("Ingresar", use_container_width=True):
            if ADMIN_PASSWORD and pwd == ADMIN_PASSWORD:
                st.session_state["is_admin"] = True
                st.rerun()
            else:
                st.error("Clave incorrecta")
    else:
        st.success("Modo administrador activo")
        if st.button("Salir de modo admin", use_container_width=True):
            st.session_state["is_admin"] = False
            st.rerun()

# ─── DATOS ───────────────────────────────────────────────────────────────────
try:
    data = data_manager.load_data()
except Exception as e:
    st.error(f"No se pudieron cargar los datos: {e}")
    st.stop()

df_pos = data["df_posiciones"]
rake_dict = data["rake_dict"]
total_rake = data["total_rake"]
camp_total, mf_total, gastos_mf = data["camp_total"], data["mf_total"], data["gastos_mf"]
fechas_info = data["fechas_info"]
schedule_data = data.get("schedule_data", [])
evento_final = data.get("evento_final", "")

jugadas = [n for n in range(1, N_FECHAS + 1) if fechas_info[n]["registrada"]]
ultima = max(jugadas) if jugadas else None
next_ev = next((s for s in schedule_data if s.get("next")), None)
has_data = (not df_pos.empty) and df_pos["Total"].sum() > 0

# ─── HEADER ──────────────────────────────────────────────────────────────────
logo_html = f'<img class="hdr-logo" src="data:image/png;base64,{logo_b64}" alt="Logo">' if logo_b64 else ""
if next_ev:
    next_html = f'<div class="hdr-next"><small>Próxima fecha</small><b>{esc(next_ev["fecha"])}</b><span>{esc(next_ev["desc"])}</span></div>'
elif evento_final:
    next_html = f'<div class="hdr-next"><small>Gran final</small><b>Mesa Final</b><span>{esc(evento_final)}</span></div>'
else:
    next_html = ""
st.markdown(f"""
<div class="hdr">
  {logo_html}
  <div><div class="hdr-title">Bingo Poker Club</div><div class="hdr-sub">Liga de Poker · Temporada 2026</div></div>
  {next_html}
</div>
""", unsafe_allow_html=True)

# ─── PODIO + FRANJA DE POZOS ─────────────────────────────────────────────────
if has_data:
    top = df_pos.head(3).to_dict("records")
    lead = int(top[0]["Total"])

    def pod(i, cls=""):
        if i >= len(top):
            return '<div class="pod"></div>'
        p = top[i]
        gap = lead - int(p["Total"])
        g = "Líder" if i == 0 else (f"a {gap} pts" if gap else "Empatado")
        return (f'<div class="pod {cls}"><div class="m">{medal(i + 1, "xl" if i == 0 else "lg")}</div><div class="n">{esc(p["Jugador"])}</div>'
                f'<div class="p">{int(p["Total"])} pts</div><div class="g">{g}</div></div>')

    st.markdown(f'<div class="podium">{pod(1)}{pod(0, "first")}{pod(2)}</div>', unsafe_allow_html=True)

st.markdown(f"""
<div class="money">
  <div class="mtot"><small>Rake total acumulado</small><b>{fmt_money(total_rake)}</b><span>{len(jugadas)} de {N_FECHAS} fechas jugadas</span></div>
  <div class="mcard"><small>🏆 Campeonato</small><em>50% del rake</em><b>{fmt_money(camp_total)}</b></div>
  <div class="mcard"><small>🃏 Mesa Final</small><em>40% del rake</em><b>{fmt_money(mf_total)}</b></div>
</div>
<div class="morg">Organización (10%): <b>{fmt_money(gastos_mf)}</b></div>
""", unsafe_allow_html=True)

# ─── TABS ────────────────────────────────────────────────────────────────────
if st.session_state["is_admin"]:
    t_pos, t_poz, t_cal, t_reg, t_jug = st.tabs(["Posiciones", "Pozos", "Calendario", "Registrar fecha", "Jugadores"])
else:
    t_pos, t_poz, t_cal = st.tabs(["Posiciones", "Pozos", "Calendario"])
    t_reg = t_jug = None

# ─── POSICIONES ──────────────────────────────────────────────────────────────
with t_pos:
    st.markdown(f'<div class="sec-title">Tabla de posiciones</div>'
                f'<div class="sec-cap">{len(jugadas)} de {N_FECHAS} fechas jugadas · puntaje acumulado</div>', unsafe_allow_html=True)
    if not has_data:
        st.markdown('<div class="empty">Aún no hay resultados. El ranking aparece después de la primera fecha.</div>', unsafe_allow_html=True)
    else:
        # Escritorio: tabla con solo las fechas jugadas
        th = "".join(
            f'<th>{n:02d}<small>{esc(fechas_info[n]["sub"]) or "&nbsp;"}</small></th>' for n in jugadas
        )
        rows = ""
        cards = ""
        for idx, r in df_pos.iterrows():
            pos = idx + 1
            cls = f"r{pos}" if pos <= 3 else ""
            badge = medal(pos)
            tds = ""
            chips = ""
            for n in jugadas:
                v = int(r.get(f"{n:02d}", 0))
                extra = " last" if n == ultima else ""
                tds += f'<td class="{"pt" if v else "z"}{extra}">{v if v else "·"}</td>'
                chips += f'<span>F{n:02d} <b>{v}</b></span>' if v else f'<span>F{n:02d} –</span>'
            name = esc(r["Jugador"])
            tot = int(r["Total"])
            rows += f'<tr class="{cls}"><td>{badge}</td><td class="l">{name}</td>{tds}<td>{tot}</td></tr>'
            lv = int(r.get(f"{ultima:02d}", 0)) if ultima else 0
            lf = f'<span class="lf">+{lv} F{ultima:02d}</span>' if lv else ""
            cards += (f'<details class="{cls}"><summary><span class="pos">{badge}</span><span class="nm">{name}</span>{lf}'
                      f'<span class="tt">{tot} pts</span></summary><div class="det">{chips}</div></details>')
        thead = f'<thead><tr><th></th><th class="l">Jugador</th>{th}<th>Total</th></tr></thead>'
        st.markdown(
            f'<table class="lb">{thead}<tbody>{rows}</tbody></table>'
            f'<div class="lbm">{cards}</div>'
            f'<details class="lbx-wrap"><summary>📋 Ver tabla completa por fecha</summary>'
            f'<div class="lbx-scroll"><table class="lb lbx">{thead}<tbody>{rows}</tbody></table></div></details>',
            unsafe_allow_html=True,
        )

    st.markdown('<div class="sec-title" style="margin-top:1.4rem">Imagen para WhatsApp</div>'
                '<div class="sec-cap">Genera la imagen oficial de la tabla para compartir en el grupo.</div>', unsafe_allow_html=True)
    if st.button("Generar imagen"):
        st.session_state["report_img"] = report_generator.generate_report_image(data)
    if "report_img" in st.session_state:
        st.image(st.session_state["report_img"], use_container_width=True)
        st.download_button("Descargar PNG", data=st.session_state["report_img"],
                           file_name="bingo_poker_club_posiciones.png", mime="image/png", use_container_width=True)

# ─── POZOS ───────────────────────────────────────────────────────────────────
with t_poz:
    st.markdown('<div class="sec-title">Distribución de premios</div>'
                '<div class="sec-cap">Según el rake acumulado de la temporada.</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="prizes">
      <div class="prize"><h4>Campeonato · 50%</h4><div class="tot">{fmt_money(camp_total)}</div>
        <div class="row"><span class="pl">{medal(1)} 1º lugar · 50%</span><b>{fmt_money(camp_total * .5)}</b></div>
        <div class="row"><span class="pl">{medal(2)} 2º lugar · 30%</span><b>{fmt_money(camp_total * .3)}</b></div>
        <div class="row"><span class="pl">{medal(3)} 3º lugar · 20%</span><b>{fmt_money(camp_total * .2)}</b></div></div>
      <div class="prize"><h4>Mesa Final · 40%</h4><div class="tot">{fmt_money(mf_total)}</div>
        <div class="row"><span class="pl">{medal(1)} 1º lugar · 50%</span><b>{fmt_money(mf_total * .5)}</b></div>
        <div class="row"><span class="pl">{medal(2)} 2º lugar · 30%</span><b>{fmt_money(mf_total * .3)}</b></div>
        <div class="row"><span class="pl">{medal(3)} 3º lugar · 20%</span><b>{fmt_money(mf_total * .2)}</b></div></div>
      <div class="prize"><h4>Organización · 10%</h4><div class="tot">{fmt_money(gastos_mf)}</div>
        <div class="row"><span>Logística y organización</span><b>10% del rake</b></div></div>
    </div>""", unsafe_allow_html=True)

    st.markdown('<div class="sec-title">Rake por fecha</div>', unsafe_allow_html=True)
    chips = ""
    for n in range(1, N_FECHAS + 1):
        v = rake_dict.get(f"F{n}", 0)
        ok = fechas_info[n]["registrada"]
        chips += f'<div class="rk {"ok" if ok else "pend"}"><small>Fecha {n:02d}</small><b>{fmt_money(v) if ok else "Pendiente"}</b></div>'
    st.markdown(f'<div class="rakes">{chips}</div>', unsafe_allow_html=True)

# ─── CALENDARIO ──────────────────────────────────────────────────────────────
with t_cal:
    st.markdown('<div class="sec-title">Calendario 2026 – 2027</div>'
                '<div class="sec-cap">Fechas que quedan de la temporada.</div>', unsafe_allow_html=True)
    if not schedule_data:
        st.markdown('<div class="empty">No quedan fechas pendientes.</div>', unsafe_allow_html=True)
    for s in schedule_data:
        badge = '<span class="badge">Próxima</span>' if s.get("next") else ""
        st.markdown(f'<div class="cal {"next" if s.get("next") else ""}"><div class="f">{esc(s["fecha"])}{badge}</div>'
                    f'<div class="d">{esc(s["desc"])}</div></div>', unsafe_allow_html=True)
    if evento_final:
        st.markdown(f'<div class="final"><h3>🏆 Gran Evento Mesa Final</h3><div>{esc(evento_final)}</div></div>', unsafe_allow_html=True)
    if st.session_state["is_admin"]:
        with st.expander("✏️ Editar Gran Evento Mesa Final"):
            with st.form("edit_final"):
                txt = st.text_input("Fecha y hora del evento", value=evento_final)
                if st.form_submit_button("Guardar"):
                    ok, err = data_manager.update_evento_final(txt.strip())
                    if ok:
                        st.session_state.pop("report_img", None)
                        st.rerun()
                    else:
                        st.error(f"Error: {err}")

# ─── REGISTRAR FECHA (ADMIN) ─────────────────────────────────────────────────
if t_reg is not None:
    with t_reg:
        # Tras guardar/borrar: limpiar estado de esa fecha y saltar a la próxima pendiente
        done = st.session_state.pop("reg_done", None)
        if done is not None:
            for k in [k for k in st.session_state.keys() if str(k).endswith(f"_{done}")]:
                del st.session_state[k]
            st.session_state.pop("reg_fecha", None)
        if "reg_msg" in st.session_state:
            st.success(st.session_state.pop("reg_msg"))

        pendientes = [n for n in range(1, N_FECHAS + 1) if not fechas_info[n]["registrada"]]
        default_n = pendientes[0] if pendientes else N_FECHAS

        def lbl(n):
            return f"Fecha {n:02d}  ·  ✅ registrada" if fechas_info[n]["registrada"] else f"Fecha {n:02d}  ·  ⏳ pendiente"

        st.markdown('<div class="sec-title">Registrar resultados</div>'
                    '<div class="sec-cap">Por defecto se abre la próxima fecha pendiente. Las fechas registradas quedan bloqueadas.</div>',
                    unsafe_allow_html=True)
        n = st.selectbox("Fecha", options=list(range(1, N_FECHAS + 1)), index=default_n - 1, format_func=lbl, key="reg_fecha")
        info = fechas_info[n]
        col = f"{n:02d}"
        actuales = df_pos[df_pos[col] > 0].sort_values(col, ascending=False) if col in df_pos else df_pos.iloc[0:0]

        locked = False
        if info["registrada"]:
            chips = "".join(f'<span>{esc(r["Jugador"])} <b>{int(r[col])}</b></span>' for _, r in actuales.iterrows()) or "<span>Sin puntos</span>"
            st.markdown(f'<div class="state ok">✅ Fecha {n:02d} ya registrada · {esc(info["tipo"] or info["sub"] or "tipo sin dato")} · '
                        f'rake {fmt_money(info["rake"])}<div class="chips">{chips}</div></div>', unsafe_allow_html=True)
            editing = st.toggle("Corregir esta fecha", key=f"reg_edit_{n}",
                                help="Actívalo solo si necesitas cambiar una fecha que ya se cargó.")
            locked = not editing
        else:
            st.markdown(f'<div class="state pend">⏳ Fecha {n:02d} pendiente. Completa los datos y guarda.</div>', unsafe_allow_html=True)

        tipos = list(data_manager.POINTS_RULES.keys())
        tipo_idx = tipos.index(info["tipo"]) if info["tipo"] in tipos else 1
        c1, c2 = st.columns(2)
        with c1:
            tipo = st.selectbox("Tipo de torneo", tipos, index=tipo_idx, key=f"reg_tipo_{n}", disabled=locked)
        with c2:
            rake = st.number_input("Rake recaudado ($)", min_value=0, step=1000, value=int(info["rake"]),
                                   key=f"reg_rake_{n}", disabled=locked)
        sub_code = "FR" if "Full ring" in tipo else ("SH" if "Shorthanded" in tipo else "MM")
        if "Main Event" in tipo:
            sub_code = "ME-" + sub_code

        # Posiciones: precargadas con lo guardado (si existe)
        players = df_pos["Jugador"].tolist()
        pre = actuales["Jugador"].tolist()
        for r in range(1, 6):
            k = f"reg_p{r}_{n}"
            if k not in st.session_state:
                st.session_state[k] = pre[r - 1] if r - 1 < len(pre) else NA

        def limpiar(fn=n):
            for r in range(1, 6):
                st.session_state[f"reg_p{r}_{fn}"] = NA

        st.markdown("**Posiciones (1º a 5º)**")
        rule = data_manager.POINTS_RULES[tipo]
        labels = ["1º lugar", "2º lugar", "3º lugar", "4º lugar", "5º lugar"]
        selections = []
        cols = st.columns(5)
        for r in range(1, 6):
            k = f"reg_p{r}_{n}"
            picked = {s for s in selections if s != NA}
            avail = [NA] + [p for p in players if p not in picked]
            if st.session_state.get(k) not in avail:
                st.session_state[k] = NA
            with cols[r - 1]:
                selections.append(st.selectbox(f"{labels[r - 1]} · {rule.get(r, 0)} pts", avail, key=k, disabled=locked))

        resultados = [{"jugador": p, "puntos": rule.get(i + 1, 0)} for i, p in enumerate(selections) if p != NA]

        if resultados:
            chips = "".join(f'<span>{i + 1}º {esc(r["jugador"])} <b>+{r["puntos"]}</b></span>' for i, r in enumerate(resultados))
            st.markdown(f'<div class="summary"><h5>Resumen antes de guardar</h5>Fecha {n:02d} · {esc(tipo)} · rake {fmt_money(rake)}'
                        f'<div class="chips">{chips}</div></div>', unsafe_allow_html=True)

        b1, b2, _ = st.columns([2, 1, 3])
        with b1:
            save = st.button("💾 Guardar fecha" if not info["registrada"] else "💾 Guardar corrección",
                             disabled=locked or not resultados, use_container_width=True)
        with b2:
            st.button("Limpiar", on_click=limpiar, disabled=locked, use_container_width=True)

        if save:
            with st.spinner("Guardando..."):
                ok, err = data_manager.save_fecha(n, tipo, sub_code, rake, resultados)
            if ok:
                st.session_state.pop("report_img", None)
                st.session_state["reg_done"] = n
                st.session_state["reg_msg"] = f"✅ Fecha {n:02d} guardada."
                st.rerun()
            else:
                st.error(f"Error al guardar: {err}")

        if info["registrada"] and not locked:
            with st.expander("🗑️ Borrar esta fecha"):
                st.warning(f"Se borran los puntos y el rake de la Fecha {n:02d} y vuelve a quedar pendiente.")
                conf = st.checkbox(f"Sí, quiero borrar la Fecha {n:02d}", key=f"reg_delconf_{n}")
                if st.button("Borrar fecha", disabled=not conf, key=f"reg_del_{n}"):
                    ok, err = data_manager.delete_fecha(n)
                    if ok:
                        st.session_state.pop("report_img", None)
                        st.session_state["reg_done"] = n
                        st.session_state["reg_msg"] = f"🗑️ Fecha {n:02d} borrada."
                        st.rerun()
                    else:
                        st.error(f"Error al borrar: {err}")

# ─── JUGADORES (ADMIN) ───────────────────────────────────────────────────────
if t_jug is not None:
    with t_jug:
        st.markdown('<div class="sec-title">Jugadores</div>', unsafe_allow_html=True)
        st.markdown('<div class="chips">' + "".join(f"<span>{esc(p)}</span>" for p in df_pos["Jugador"]) + "</div>",
                    unsafe_allow_html=True)
        with st.form("add_player", clear_on_submit=True):
            nuevo = st.text_input("Nombre del nuevo jugador")
            if st.form_submit_button("➕ Agregar jugador"):
                nombre = (nuevo or "").strip()
                if not nombre:
                    st.warning("Escribe un nombre.")
                elif nombre.lower() in [p.lower() for p in df_pos["Jugador"]]:
                    st.warning("Ese jugador ya existe.")
                else:
                    ok, err = data_manager.add_player(nombre)
                    if ok:
                        st.success(f"Jugador {nombre} agregado.")
                        st.rerun()
                    else:
                        st.error(f"Error: {err}")

st.markdown('<div class="foot">Temporada <b>2026</b> · <b>Bingo Poker Club</b> · Liga de Poker Chile</div>', unsafe_allow_html=True)
