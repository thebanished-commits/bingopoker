import streamlit as st
import pandas as pd
import os
import base64
import data_manager
import report_generator

st.set_page_config(
    page_title="Bingo Poker Club 2026",
    page_icon="🏆",
    layout="wide",
    initial_sidebar_state="collapsed"
)

FECHAS_STANDARD = [f"{i:02d}" for i in range(1, 11)]

def fmt_money(val):
    try:
        return f"${int(val):,}".replace(",", ".")
    except Exception:
        return "$0"

def get_logo_b64():
    p_small = os.path.join(os.path.dirname(__file__), 'assets', 'logo_small.png')
    p_main = os.path.join(os.path.dirname(__file__), 'assets', 'logo.png')
    target = p_small if os.path.exists(p_small) else (p_main if os.path.exists(p_main) else None)
    if target:
        try:
            with open(target, 'rb') as f:
                return base64.b64encode(f.read()).decode()
        except Exception:
            return None
    return None

logo_b64 = get_logo_b64()
ADMIN_PASSWORD = "admin123"

if "is_admin" not in st.session_state:
    st.session_state["is_admin"] = False

# Inject favicon from logo
if logo_b64:
    st.markdown(f"""
    <link rel="icon" type="image/png" href="data:image/png;base64,{logo_b64}">
    <script>
        var link = document.querySelector("link[rel~='icon']");
        if (!link) {{ link = document.createElement('link'); link.rel = 'icon'; document.head.appendChild(link); }}
        link.href = "data:image/png;base64,{logo_b64}";
    </script>
    """, unsafe_allow_html=True)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@700;800&family=Plus+Jakarta+Sans:wght@600;700;800&display=swap');

    .stApp {
        background: radial-gradient(circle at 50% 0%, #1e1b4b 0%, #0f172a 45%, #070b14 100%) !important;
        font-family: 'Plus Jakarta Sans', sans-serif;
        color: #f8fafc;
    }

    /* Main Header */
    .main-header {
        background: linear-gradient(135deg, rgba(30, 27, 75, 0.95) 0%, rgba(15, 23, 42, 0.95) 50%, rgba(180, 83, 9, 0.25) 100%);
        border: 2px solid #f59e0b;
        box-shadow: 0 8px 25px rgba(245, 158, 11, 0.2), inset 0 1px 1px rgba(255, 255, 255, 0.15);
        border-radius: 14px;
        padding: 0.85rem 1rem;
        text-align: center;
        margin-bottom: 1.2rem;
        backdrop-filter: blur(10px);
    }
    .main-title {
        font-family: 'Outfit', sans-serif;
        background: linear-gradient(135deg, #fffbeb 0%, #facc15 40%, #f59e0b 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        font-size: 1.85rem;
        margin: 0 0 4px 0;
        letter-spacing: 1.5px;
    }
    .sub-title {
        color: #fbbf24;
        font-size: 1.05rem;
        font-weight: 700;
        margin-top: 2px;
        letter-spacing: 1px;
        text-transform: uppercase;
    }

    /* Metric Cards */
    div[data-testid="stMetric"] {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.85) 0%, rgba(15, 23, 42, 0.95) 100%);
        border: 1px solid rgba(245, 158, 11, 0.35);
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.4);
        border-radius: 14px;
        padding: 12px;
        transition: all 0.3s ease;
    }
    div[data-testid="stMetric"]:hover {
        border-color: #f59e0b;
        box-shadow: 0 8px 25px rgba(245, 158, 11, 0.35);
        transform: translateY(-2px);
    }
    div[data-testid="stMetricLabel"] {
        color: #cbd5e1 !important;
        font-size: 0.9rem !important;
        font-weight: 700 !important;
        text-transform: uppercase;
    }
    div[data-testid="stMetricValue"] {
        font-family: 'Outfit', sans-serif !important;
        font-size: 1.6rem !important;
        background: linear-gradient(135deg, #ffffff 0%, #fbbf24 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800 !important;
    }

    /* Prize Breakdown Cards */
    .prize-container {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        gap: 14px;
        margin: 1rem 0 1.5rem 0;
    }
    .prize-card {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.9) 0%, rgba(15, 23, 42, 0.95) 100%);
        border: 1px solid rgba(245, 158, 11, 0.4);
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.4);
        border-radius: 14px;
        padding: 16px;
        transition: all 0.3s ease;
    }
    .prize-card:hover { border-color: #f59e0b; transform: translateY(-2px); }
    .prize-card-title { color: #facc15; font-weight: 800; font-size: 0.9rem; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 4px; }
    .prize-card-total { font-family: 'Outfit', sans-serif; font-size: 1.55rem; font-weight: 800; color: #ffffff; margin-bottom: 8px; border-bottom: 1px solid rgba(245, 158, 11, 0.2); padding-bottom: 6px; }
    .prize-row { display: flex; justify-content: space-between; align-items: center; padding: 5px 0; font-size: 0.93rem; border-bottom: 1px solid rgba(255, 255, 255, 0.05); }
    .prize-row:last-child { border-bottom: none; }
    .prize-row span { color: #cbd5e1; font-weight: 600; }
    .prize-row strong { color: #fbbf24; font-weight: 800; font-size: 1.02rem; }

    /* Gold Metallic Tab Buttons */
    .stTabs [data-baseweb="tab-list"] {
        gap: 14px !important;
        background: transparent !important;
        border-bottom: 2px solid rgba(245, 158, 11, 0.25) !important;
        padding-bottom: 12px !important;
    }
    .stTabs [data-baseweb="tab"], .stTabs button[role="tab"] {
        padding: 10px 24px !important;
        background: rgba(15, 23, 42, 0.85) !important;
        border-radius: 12px !important;
        color: #f8fafc !important;
        font-weight: 700 !important;
        font-size: 1.05rem !important;
        border: 2px solid rgba(245, 158, 11, 0.4) !important;
        transition: all 0.25s ease !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.4) !important;
        margin-right: 4px !important;
    }
    .stTabs [data-baseweb="tab"]:hover, .stTabs button[role="tab"]:hover {
        background: rgba(30, 41, 59, 0.95) !important;
        color: #facc15 !important;
        border-color: #f59e0b !important;
        transform: translateY(-2px) !important;
    }
    .stTabs [aria-selected="true"], .stTabs button[aria-selected="true"] {
        background: linear-gradient(135deg, #f59e0b 0%, #d97706 50%, #b45309 100%) !important;
        color: #ffffff !important;
        font-weight: 800 !important;
        border-radius: 12px !important;
        border: 2px solid #fef08a !important;
        box-shadow: 0 6px 22px rgba(245, 158, 11, 0.5) !important;
        text-shadow: 0 1px 3px rgba(0, 0, 0, 0.7) !important;
    }
    .stTabs [data-baseweb="tab-highlight"], div[data-baseweb="tab-highlight"],
    div[data-baseweb="tab-border"], .stTabs [data-baseweb="tab-list"] > div[style*="background-color"] {
        display: none !important; visibility: hidden !important; height: 0px !important;
        opacity: 0 !important; background: transparent !important; border: none !important;
    }

    /* Action Buttons */
    .stButton>button {
        background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%) !important;
        color: #0f172a !important; font-weight: 800 !important; font-size: 1.05rem !important;
        border: none !important; border-radius: 12px !important; padding: 0.8rem 1.6rem !important;
        box-shadow: 0 4px 15px rgba(245, 158, 11, 0.35) !important; letter-spacing: 0.5px;
    }
    .stButton>button:hover {
        background: linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%) !important;
        box-shadow: 0 6px 20px rgba(245, 158, 11, 0.5) !important; transform: translateY(-1px);
    }

    /* Dataframe */
    .stDataFrame { border-radius: 12px; overflow: hidden; border: 1px solid rgba(245, 158, 11, 0.3); box-shadow: 0 8px 25px rgba(0,0,0,0.5); }

    /* Leaderboard Table */
    .leaderboard-table { width: 100%; border-collapse: separate; border-spacing: 0 8px; margin: 0.8rem 0; }
    .leaderboard-table th {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.95) 0%, rgba(15, 23, 42, 0.95) 100%);
        color: #fbbf24; font-weight: 800; font-size: 0.88rem; padding: 10px 8px; text-align: center;
        border-top: 1px solid rgba(245, 158, 11, 0.3); border-bottom: 1px solid rgba(245, 158, 11, 0.3);
        text-transform: uppercase; letter-spacing: 0.5px;
    }
    .leaderboard-table th:first-child { border-top-left-radius: 10px; border-bottom-left-radius: 10px; border-left: 1px solid rgba(245, 158, 11, 0.3); text-align: left; padding-left: 14px; }
    .leaderboard-table th:last-child { border-top-right-radius: 10px; border-bottom-right-radius: 10px; border-right: 1px solid rgba(245, 158, 11, 0.3); }
    .leaderboard-row { background: linear-gradient(135deg, rgba(30, 41, 59, 0.8) 0%, rgba(15, 23, 42, 0.9) 100%); border: 1px solid rgba(245, 158, 11, 0.2); box-shadow: 0 4px 12px rgba(0,0,0,0.3); transition: all 0.3s ease; }
    .leaderboard-row:hover { border-color: #f59e0b; transform: translateY(-1px); box-shadow: 0 6px 18px rgba(245, 158, 11, 0.2); }
    .leaderboard-row td { padding: 10px 8px; text-align: center; font-size: 0.95rem; color: #f8fafc; font-weight: 600; }
    .leaderboard-row td:first-child { border-top-left-radius: 10px; border-bottom-left-radius: 10px; text-align: left; padding-left: 14px; font-weight: 800; }
    .leaderboard-row td:last-child { border-top-right-radius: 10px; border-bottom-right-radius: 10px; font-family: 'Outfit', sans-serif; font-size: 1.15rem; font-weight: 800; color: #facc15; }
    .rank-1 { background: linear-gradient(135deg, rgba(180, 83, 9, 0.35) 0%, rgba(30, 41, 59, 0.95) 100%) !important; border: 2px solid #f59e0b !important; }
    .rank-2 { background: linear-gradient(135deg, rgba(100, 116, 139, 0.35) 0%, rgba(30, 41, 59, 0.95) 100%) !important; border: 1.5px solid #94a3b8 !important; }
    .rank-3 { background: linear-gradient(135deg, rgba(180, 83, 9, 0.2) 0%, rgba(30, 41, 59, 0.95) 100%) !important; border: 1.5px solid #d97706 !important; }
    .pts-active { color: #4ade80 !important; font-weight: 800 !important; }
    .pts-zero { color: #1e3a5f !important; font-size: 0.75rem !important; }

    /* Empty State */
    .empty-state {
        text-align: center; padding: 30px 20px;
        background: rgba(15, 23, 42, 0.6); border: 1px dashed rgba(245, 158, 11, 0.3);
        border-radius: 14px; color: #64748b; font-size: 0.95rem; font-weight: 600; margin: 1rem 0;
    }
    .empty-state .empty-icon { font-size: 2.5rem; display: block; margin-bottom: 8px; }

    /* Rake Chips Grid */
    .rake-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(130px, 1fr)); gap: 14px; margin: 1rem 0 2rem 0; }
    .rake-chip { background: linear-gradient(135deg, rgba(30, 41, 59, 0.9) 0%, rgba(15, 23, 42, 0.95) 100%); border: 1px solid rgba(245, 158, 11, 0.3); border-radius: 12px; padding: 14px 10px; text-align: center; box-shadow: 0 4px 12px rgba(0,0,0,0.3); }
    .rake-chip-active { border: 2px solid #22c55e !important; box-shadow: 0 0 15px rgba(34, 197, 94, 0.25) !important; }
    .rake-chip-title { color: #94a3b8; font-size: 0.85rem; font-weight: 700; text-transform: uppercase; margin-bottom: 4px; }
    .rake-chip-val { font-family: 'Outfit', sans-serif; font-size: 1.3rem; font-weight: 800; color: #facc15; }
    .rake-status-badge { display: inline-block; margin-top: 6px; font-size: 0.75rem; font-weight: 800; padding: 2px 8px; border-radius: 10px; }
    .status-ok { background: rgba(34, 197, 94, 0.2); color: #4ade80; border: 1px solid #22c55e; }
    .status-wait { background: rgba(148, 163, 184, 0.1); color: #94a3b8; border: 1px solid #475569; }

    /* Calendar */
    .cal-card { background: linear-gradient(135deg, rgba(30, 41, 59, 0.9) 0%, rgba(15, 23, 42, 0.95) 100%); border: 1px solid rgba(245, 158, 11, 0.3); border-radius: 14px; padding: 16px; margin-bottom: 12px; display: flex; justify-content: space-between; align-items: center; transition: all 0.3s ease; }
    .cal-card:hover { border-color: #f59e0b; box-shadow: 0 4px 20px rgba(245, 158, 11, 0.25); }
    .cal-next { border: 2px solid #f59e0b !important; background: linear-gradient(135deg, rgba(180, 83, 9, 0.25) 0%, rgba(30, 41, 59, 0.95) 100%) !important; box-shadow: 0 0 20px rgba(245, 158, 11, 0.3) !important; }
    .cal-num { font-family: 'Outfit', sans-serif; font-size: 1.4rem; font-weight: 800; color: #facc15; min-width: 100px; }
    .cal-desc { font-size: 1.1rem; font-weight: 700; color: #f8fafc; }
    .cal-badge { background: #f59e0b; color: #0f172a; font-weight: 800; font-size: 0.8rem; padding: 4px 10px; border-radius: 20px; text-transform: uppercase; letter-spacing: 0.5px; margin-left: 10px; }
    .cal-final { background: linear-gradient(135deg, #1e1b4b 0%, rgba(180, 83, 9, 0.4) 100%) !important; border: 2px solid #fbbf24 !important; box-shadow: 0 8px 30px rgba(251, 191, 36, 0.35) !important; padding: 20px !important; border-radius: 16px !important; text-align: center; margin-top: 20px; }
    .cal-final-title { font-family: 'Outfit', sans-serif; font-size: 1.5rem; font-weight: 800; color: #fbbf24; margin-bottom: 6px; letter-spacing: 1px; }
    .cal-final-desc { font-size: 1.2rem; font-weight: 700; color: #ffffff; }

    /* Footer */
    .app-footer {
        text-align: center;
        margin-top: 3rem;
        padding: 1.2rem;
        border-top: 1px solid rgba(245, 158, 11, 0.2);
        color: #475569;
        font-size: 0.85rem;
        font-weight: 600;
        letter-spacing: 0.5px;
    }
    .app-footer span { color: #f59e0b; }

    /* Mobile */
    @media (max-width: 768px) {
        .main-title { font-size: 1.4rem; }
        .sub-title { font-size: 0.95rem; }
        div[data-testid="stMetricValue"] { font-size: 1.3rem !important; }
        .stTabs [data-baseweb="tab"], .stTabs button[role="tab"] { padding: 8px 14px !important; font-size: 0.9rem !important; border-radius: 10px !important; }
        .cal-card { flex-direction: column; align-items: flex-start; gap: 6px; }
        .rake-chip-val { font-size: 1.1rem; }
        .leaderboard-table th, .leaderboard-row td { padding: 8px 4px; font-size: 0.8rem; }
    }
</style>
""", unsafe_allow_html=True)

# Sidebar admin login
st.sidebar.title("🔐 Acceso Administrador")
if not st.session_state["is_admin"]:
    input_pass = st.sidebar.text_input("Ingresa la clave de administrador:", type="password")
    if st.sidebar.button("Ingresar como Admin"):
        if input_pass == ADMIN_PASSWORD:
            st.session_state["is_admin"] = True
            st.sidebar.success("¡Acceso concedido!")
            st.rerun()
        else:
            st.sidebar.error("Clave incorrecta")
else:
    st.sidebar.success("🟢 MODO ADMINISTRADOR ACTIVO")
    if st.sidebar.button("🔒 Salir de Modo Admin"):
        st.session_state["is_admin"] = False
        st.rerun()

# Header
logo_html = f'<img src="data:image/png;base64,{logo_b64}" style="max-width:80px !important; width:80px !important; height:auto !important; display:block; margin:4px auto 6px auto; filter:drop-shadow(0 0 10px rgba(245,158,11,0.4));" alt="Logo">' if logo_b64 else ''
st.markdown(f"""
<div class="main-header">
    <h1 class="main-title">BINGO POKER CLUB 2026</h1>
    {logo_html}
    <div class="sub-title">Liga Oficial de Poker · Chile</div>
</div>
""", unsafe_allow_html=True)

data = data_manager.load_data()
df_pos = data["df_posiciones"]
rake_dict = data["rake_dict"]
total_rake = data["total_rake"]
camp_total = data.get("camp_total", total_rake * 0.50)
mf_total = data.get("mf_total", total_rake * 0.40)
gastos_mf = data.get("gastos_mf", total_rake * 0.10)
payouts = data["payouts"]
subheaders = data["subheaders"]

# 4 Metric Cards — Portada compacta
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.metric("💰 Rake Total", fmt_money(total_rake))
with c2:
    st.metric("🏆 Campeonato (50%)", fmt_money(camp_total))
with c3:
    st.metric("🃏 Mesa Final (40%)", fmt_money(mf_total))
with c4:
    st.metric("🧾 Fondo Organización (10%)", fmt_money(gastos_mf))

st.write("---")

# Tabs
if st.session_state["is_admin"]:
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["🏆 Posiciones", "📝 Registrar Fecha", "💵 Rake & Pozos", "⚙️ Jugadores", "📅 Calendario"])
else:
    tab1, tab3, tab5 = st.tabs(["🏆 Posiciones", "💵 Rake & Pozos", "📅 Calendario"])
    tab2, tab4 = None, None

# ─── TAB 1: POSICIONES ──────────────────────────────────────────────────────
with tab1:
    st.subheader("🏆 Tabla de Posiciones General")
    st.caption("Puntaje acumulado fecha a fecha · Temporada 2026 (10 Fechas)")

    # Check if all totals are 0
    has_data = df_pos["Total"].sum() > 0

    if not has_data:
        st.markdown("""
        <div class="empty-state">
            <span class="empty-icon">🎴</span>
            Aún no se han registrado resultados.<br>El ranking aparecerá aquí luego de la primera fecha.
        </div>
        """, unsafe_allow_html=True)
    else:
        lead_html = '<table class="leaderboard-table"><thead><tr><th>Jugador</th>'
        for f in FECHAS_STANDARD:
            lead_html += f'<th>{f}</th>'
        lead_html += '<th>Total</th></tr></thead><tbody>'

        medals_map = {1: "🥇", 2: "🥈", 3: "🥉"}
        for idx, row in df_pos.iterrows():
            pos_num = idx + 1
            row_cls = "leaderboard-row rank-1" if pos_num == 1 else ("leaderboard-row rank-2" if pos_num == 2 else ("leaderboard-row rank-3" if pos_num == 3 else "leaderboard-row"))
            medal = medals_map.get(pos_num, f"{pos_num}º")
            lead_html += f'<tr class="{row_cls}"><td>{medal} {row["Jugador"]}</td>'
            for f in FECHAS_STANDARD:
                val = int(row.get(f, 0))
                val_cls = "pts-active" if val > 0 else "pts-zero"
                cell_txt = str(val) if val > 0 else "—"
                lead_html += f'<td class="{val_cls}">{cell_txt}</td>'
            lead_html += f'<td>{int(row["Total"])} pts</td></tr>'
        lead_html += '</tbody></table>'
        st.markdown(lead_html, unsafe_allow_html=True)

    st.write("---")
    st.subheader("📸 Reporte para WhatsApp")
    st.caption("Genera y descarga la imagen oficial optimizada para compartir en grupos de WhatsApp.")
    col_img_btn, _ = st.columns([1, 1])
    with col_img_btn:
        if st.button("🖼️ Generar Imagen HD para WhatsApp"):
            img_bytes = report_generator.generate_report_image(data)
            st.session_state["report_img"] = img_bytes
            st.success("¡Imagen generada con éxito!")
    if "report_img" in st.session_state:
        st.image(st.session_state["report_img"], caption="Reporte Oficial Bingo Poker Club 2026", use_container_width=True)
        st.download_button(label="📥 Descargar PNG para WhatsApp", data=st.session_state["report_img"], file_name="bingo_poker_club_posiciones.png", mime="image/png", use_container_width=True)

# ─── TAB 3: RAKE & POZOS ────────────────────────────────────────────────────
with tab3:
    st.subheader("💰 Distribución de Premios")
    st.caption("Desglose de pozos según el rake acumulado de la temporada.")

    st.markdown(f"""
    <div class="prize-container">
        <div class="prize-card">
            <div class="prize-card-title">🏆 PREMIOS CAMPEONATO (50%)</div>
            <div class="prize-card-total">{fmt_money(camp_total)}</div>
            <div class="prize-row"><span>🥇 1º Lugar (50%)</span><strong>{fmt_money(camp_total * 0.50)}</strong></div>
            <div class="prize-row"><span>🥈 2º Lugar (30%)</span><strong>{fmt_money(camp_total * 0.30)}</strong></div>
            <div class="prize-row"><span>🥉 3º Lugar (20%)</span><strong>{fmt_money(camp_total * 0.20)}</strong></div>
        </div>
        <div class="prize-card">
            <div class="prize-card-title">🃏 PREMIOS MESA FINAL (40%)</div>
            <div class="prize-card-total">{fmt_money(mf_total)}</div>
            <div class="prize-row"><span>🥇 1º Lugar (50%)</span><strong>{fmt_money(mf_total * 0.50)}</strong></div>
            <div class="prize-row"><span>🥈 2º Lugar (30%)</span><strong>{fmt_money(mf_total * 0.30)}</strong></div>
            <div class="prize-row"><span>🥉 3º Lugar (20%)</span><strong>{fmt_money(mf_total * 0.20)}</strong></div>
        </div>
        <div class="prize-card">
            <div class="prize-card-title">🧾 FONDO ORGANIZACIÓN (10%)</div>
            <div class="prize-card-total">{fmt_money(gastos_mf)}</div>
            <div class="prize-row"><span>Logística & Organización</span><strong>10% Rake</strong></div>
            <div class="prize-row"><span>Acumulado temporada</span><strong>{fmt_money(gastos_mf)}</strong></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.write("---")
    st.subheader("💵 Control de Rake por Fecha")
    st.caption("Monto recaudado en cada fecha de la temporada.")

    chips_html = '<div class="rake-grid">'
    for i in range(1, 11):
        f_key = f"F{i}"
        val = rake_dict.get(f_key, 0)
        is_active = val > 0
        card_cls = "rake-chip rake-chip-active" if is_active else "rake-chip"
        badge_cls = "rake-status-badge status-ok" if is_active else "rake-status-badge status-wait"
        status_txt = "Recaudado" if is_active else "Pendiente"
        val_txt = fmt_money(val) if is_active else "$0"
        chips_html += f'<div class="{card_cls}"><div class="rake-chip-title">Fecha {i:02d}</div><div class="rake-chip-val">{val_txt}</div><div class="{badge_cls}">{status_txt}</div></div>'
    chips_html += '</div>'
    st.markdown(chips_html, unsafe_allow_html=True)

# ─── TAB 5: CALENDARIO ──────────────────────────────────────────────────────
with tab5:
    st.subheader("📅 Calendario Oficial 2026 – 2027")
    st.caption("Programación de la temporada, leída en vivo desde Google Sheets.")

    schedule_data = data.get("schedule_data", [])
    evento_final = data.get("evento_final", "Sábado 09 de Enero 2027 desde las 14 horas")

    if not schedule_data:
        st.markdown('<div class="empty-state"><span class="empty-icon">📅</span>No hay fechas cargadas en el Calendario de Google Sheets aún.</div>', unsafe_allow_html=True)
    else:
        for s in schedule_data:
            card_class = "cal-card cal-next" if s.get("next") else "cal-card"
            badge_html = '<span class="cal-badge">🔥 Próximo Torneo</span>' if s.get("next") else ''
            st.markdown(f'<div class="{card_class}"><div class="cal-num">{s["fecha"]} {badge_html}</div><div class="cal-desc">🗓️ {s["desc"]}</div></div>', unsafe_allow_html=True)

    st.markdown(f"""
    <div class="cal-final">
        <div class="cal-final-title">🏆 GRAN EVENTO MESA FINAL</div>
        <div class="cal-final-desc">🗓️ {evento_final}</div>
    </div>
    """, unsafe_allow_html=True)

# ─── TAB 2: REGISTRAR FECHA (ADMIN) ─────────────────────────────────────────
if st.session_state["is_admin"] and tab2:
    with tab2:
        st.subheader("📝 Ingreso de Resultados por Fecha")
        fecha_num = st.selectbox("Seleccionar Fecha", options=FECHAS_STANDARD, index=0)
        f_index = int(fecha_num) - 1
        tourn_type = st.selectbox("Tipo de Torneo", options=list(data_manager.POINTS_RULES.keys()), index=1)
        sub_code = "FR" if "Full ring" in tourn_type else ("SH" if "Shorthanded" in tourn_type else "MM")
        if "Main Event" in tourn_type:
            sub_code = "ME-" + sub_code
        current_rake = rake_dict.get(f"F{int(fecha_num)}", 0)
        new_rake = st.number_input(f"Rake Recaudado en Fecha {fecha_num} ($)", min_value=0, value=int(current_rake), step=1000)

        with st.expander("🔍 Debug — Jugadores cargados desde Google Sheets"):
            st.write(df_pos["Jugador"].tolist())

        all_players = df_pos["Jugador"].tolist()
        NA = "-- Seleccionar --"

        # ── Auto-reset selecciones al cambiar de fecha ──────────────────────
        last_fecha_key = "reg_last_fecha"
        if st.session_state.get(last_fecha_key) != fecha_num:
            # La fecha cambió → limpiar todas las posiciones anteriores
            for prev_r in range(1, 6):
                for prev_f in FECHAS_STANDARD:
                    k = f"reg_pos{prev_r}_{prev_f}"
                    if k in st.session_state:
                        del st.session_state[k]
            st.session_state[last_fecha_key] = fecha_num

        # Inicializar claves si no existen
        for r in range(1, 6):
            key = f"reg_pos{r}_{fecha_num}"
            if key not in st.session_state:
                st.session_state[key] = NA

        # Botón limpiar manual
        col_lbl, col_btn = st.columns([3, 1])
        with col_lbl:
            st.write("#### Asignación de Posiciones (1° al 5° lugar)")
        with col_btn:
            if st.button("🔄 Limpiar", help="Borra todas las selecciones"):
                for r in range(1, 6):
                    k = f"reg_pos{r}_{fecha_num}"
                    if k in st.session_state:
                        del st.session_state[k]
                st.rerun()

        # Dropdowns en cascada: cada uno excluye los ya elegidos antes
        selections = []
        labels = ["🥇 1er Lugar", "🥈 2do Lugar", "🥉 3er Lugar", "4to Lugar", "5to Lugar"]
        for r in range(1, 6):
            key = f"reg_pos{r}_{fecha_num}"
            already_picked = {
                st.session_state[f"reg_pos{prev}_{fecha_num}"]
                for prev in range(1, r)
                if st.session_state.get(f"reg_pos{prev}_{fecha_num}", NA) != NA
            }
            available = [NA] + [p for p in all_players if p not in already_picked]
            sel = st.selectbox(labels[r-1], options=available,
                               key=key, index=available.index(st.session_state[key]))
            selections.append(sel)

        if st.button("💾 Guardar y Actualizar Fecha"):
            pts_rule = data_manager.POINTS_RULES[tourn_type]
            for idx in range(len(df_pos)):
                df_pos.at[idx, fecha_num] = 0
            for rank_idx, p_name in enumerate(selections):
                if p_name and p_name != NA:
                    pts = pts_rule.get(rank_idx + 1, 0)
                    p_mask = df_pos["Jugador"] == p_name
                    if p_mask.any():
                        p_i = df_pos[p_mask].index[0]
                        df_pos.at[p_i, fecha_num] = pts
            df_pos["Total"] = df_pos[FECHAS_STANDARD].sum(axis=1)
            df_pos = df_pos.sort_values(by="Total", ascending=False).reset_index(drop=True)
            df_pos["Pos"] = range(1, len(df_pos) + 1)
            if f_index < len(subheaders):
                subheaders[f_index] = sub_code
            rake_dict[f"F{int(fecha_num)}"] = new_rake
            with st.spinner("Guardando..."):
                result = data_manager.save_data(df_pos, rake_dict, subheaders)
                if isinstance(result, tuple):
                    ok, err = result
                else:
                    ok, err = bool(result), None
            if ok:
                st.success(f"✅ ¡Fecha {fecha_num} guardada exitosamente!")
                st.rerun()
            else:
                st.error(f"❌ Error al guardar: {err}")
                st.info("💡 Asegúrate de haber subido `data_manager.py` actualizado a GitHub.")


# ─── TAB 4: JUGADORES (ADMIN) ───────────────────────────────────────────────
if st.session_state["is_admin"] and tab4:
    with tab4:
        st.subheader("👤 Administración de Jugadores")
        new_p_name = st.text_input("Nombre de Nuevo Jugador")
        if st.button("➕ Agregar Jugador"):
            if new_p_name and new_p_name.strip():
                p_clean = new_p_name.strip()
                if p_clean not in df_pos["Jugador"].values:
                    new_row = {"Pos": len(df_pos) + 1, "Jugador": p_clean, "Total": 0}
                    for f in FECHAS_STANDARD:
                        new_row[f] = 0
                    df_pos = pd.concat([df_pos, pd.DataFrame([new_row])], ignore_index=True)
                    ok, err = data_manager.save_data(df_pos, rake_dict, subheaders)
                    if ok:
                        st.success(f"✅ Jugador '{p_clean}' agregado con éxito.")
                        st.rerun()
                    else:
                        st.error(f"❌ Error al guardar jugador: {err}")
                else:
                    st.warning("El jugador ya existe.")

# ─── FOOTER ─────────────────────────────────────────────────────────────────
st.markdown("""
<div class="app-footer">
    Temporada <span>2026</span> · <span>Bingo Poker Club</span> · Liga Oficial de Poker Chile 🃏<br>
    <small style="opacity:0.5;">Datos actualizados en tiempo real desde Google Sheets</small>
</div>
""", unsafe_allow_html=True)
