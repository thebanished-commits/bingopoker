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

# Custom High-End Casino Velvet & Gold Theme
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@700;800&family=Plus+Jakarta+Sans:wght@500;700;800&display=swap');

    .stApp {
        background: radial-gradient(circle at 50% 0%, #1e1b4b 0%, #0f172a 45%, #070b14 100%) !important;
        font-family: 'Plus Jakarta Sans', sans-serif;
        color: #f8fafc;
    }
    
    /* Main Unified Header Banner */
    .main-header {
        background: linear-gradient(135deg, rgba(30, 27, 75, 0.95) 0%, rgba(15, 23, 42, 0.95) 50%, rgba(180, 83, 9, 0.25) 100%);
        border: 2px solid #f59e0b;
        box-shadow: 0 10px 30px rgba(245, 158, 11, 0.25), inset 0 1px 1px rgba(255, 255, 255, 0.2);
        border-radius: 16px;
        padding: 1.5rem 1rem;
        text-align: center;
        margin-bottom: 1.5rem;
        backdrop-filter: blur(10px);
    }
    .main-title {
        font-family: 'Outfit', sans-serif;
        background: linear-gradient(135deg, #fffbeb 0%, #facc15 40%, #f59e0b 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        font-size: 2.2rem;
        margin: 0 0 10px 0;
        letter-spacing: 2px;
        text-shadow: 0 2px 10px rgba(0, 0, 0, 0.5);
    }
    .sub-title {
        color: #fbbf24;
        font-size: 1.25rem;
        font-weight: 700;
        margin-top: 4px;
        letter-spacing: 1px;
        text-transform: uppercase;
    }
    
    /* Metric Cards */
    div[data-testid="stMetric"] {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.85) 0%, rgba(15, 23, 42, 0.95) 100%);
        border: 1px solid rgba(245, 158, 11, 0.35);
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.4);
        border-radius: 14px;
        padding: 14px;
        transition: all 0.3s ease;
    }
    div[data-testid="stMetric"]:hover {
        border-color: #f59e0b;
        box-shadow: 0 8px 25px rgba(245, 158, 11, 0.35);
        transform: translateY(-2px);
    }
    div[data-testid="stMetricLabel"] {
        color: #94a3b8 !important;
        font-size: 0.85rem !important;
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
    
    /* Prize Breakdown Component */
    .prize-container {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        gap: 16px;
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
    .prize-card:hover {
        border-color: #f59e0b;
        transform: translateY(-2px);
    }
    .prize-card-title {
        color: #facc15;
        font-weight: 800;
        font-size: 0.95rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 4px;
    }
    .prize-card-total {
        font-family: 'Outfit', sans-serif;
        font-size: 1.5rem;
        font-weight: 800;
        color: #ffffff;
        margin-bottom: 10px;
        border-bottom: 1px solid rgba(245, 158, 11, 0.2);
        padding-bottom: 6px;
    }
    .prize-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 5px 0;
        font-size: 0.9rem;
        border-bottom: 1px solid rgba(255, 255, 255, 0.05);
    }
    .prize-row:last-child {
        border-bottom: none;
    }
    .prize-row span {
        color: #cbd5e1;
        font-weight: 600;
    }
    .prize-row strong {
        color: #fbbf24;
        font-weight: 800;
        font-size: 1rem;
    }

    /* Fully Rounded Pill Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 12px !important;
        background: transparent !important;
        border-bottom: 2px solid rgba(245, 158, 11, 0.2) !important;
        padding-bottom: 10px !important;
    }
    .stTabs [data-baseweb="tab"], .stTabs button[role="tab"] {
        padding: 10px 24px !important;
        background: rgba(30, 41, 59, 0.75) !important;
        border-radius: 30px !important;
        color: #cbd5e1 !important;
        font-weight: 700 !important;
        font-size: 0.95rem !important;
        border: 1px solid rgba(245, 158, 11, 0.25) !important;
        transition: all 0.25s ease !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.3) !important;
    }
    .stTabs [data-baseweb="tab"]:hover, .stTabs button[role="tab"]:hover {
        background: rgba(45, 60, 85, 0.9) !important;
        color: #facc15 !important;
        border-color: #f59e0b !important;
    }
    .stTabs [aria-selected="true"], .stTabs button[aria-selected="true"] {
        background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%) !important;
        color: #0f172a !important;
        font-weight: 800 !important;
        border-radius: 30px !important;
        border-color: #fbbf24 !important;
        box-shadow: 0 4px 15px rgba(245, 158, 11, 0.45) !important;
    }
    .stTabs [data-baseweb="tab-highlight"], div[data-baseweb="tab-highlight"] {
        display: none !important;
        height: 0px !important;
        background-color: transparent !important;
    }
    .stTabs [data-baseweb="tab-border"] {
        display: none !important;
    }
    
    /* Action Buttons */
    .stButton>button {
        background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%) !important;
        color: #0f172a !important;
        font-weight: 800 !important;
        font-size: 1.05rem !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.75rem 1.5rem !important;
        box-shadow: 0 4px 15px rgba(245, 158, 11, 0.35) !important;
        letter-spacing: 0.5px;
    }
    .stButton>button:hover {
        background: linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%) !important;
        box-shadow: 0 6px 20px rgba(245, 158, 11, 0.5) !important;
        transform: translateY(-1px);
    }
    
    /* Dataframe Container */
    .stDataFrame {
        border-radius: 12px;
        overflow: hidden;
        border: 1px solid rgba(245, 158, 11, 0.3);
        box-shadow: 0 8px 25px rgba(0,0,0,0.5);
    }

    /* Calendar Styling */
    .cal-card {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.9) 0%, rgba(15, 23, 42, 0.95) 100%);
        border: 1px solid rgba(245, 158, 11, 0.3);
        border-radius: 14px;
        padding: 16px;
        margin-bottom: 12px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        transition: all 0.3s ease;
    }
    .cal-card:hover {
        border-color: #f59e0b;
        box-shadow: 0 4px 20px rgba(245, 158, 11, 0.25);
    }
    .cal-next {
        border: 2px solid #f59e0b !important;
        background: linear-gradient(135deg, rgba(180, 83, 9, 0.25) 0%, rgba(30, 41, 59, 0.95) 100%) !important;
        box-shadow: 0 0 20px rgba(245, 158, 11, 0.3) !important;
    }
    .cal-num {
        font-family: 'Outfit', sans-serif;
        font-size: 1.4rem;
        font-weight: 800;
        color: #facc15;
        min-width: 90px;
    }
    .cal-desc {
        font-size: 1.1rem;
        font-weight: 700;
        color: #f8fafc;
    }
    .cal-badge {
        background: #f59e0b;
        color: #0f172a;
        font-weight: 800;
        font-size: 0.8rem;
        padding: 4px 10px;
        border-radius: 20px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-left: 10px;
    }
    .cal-final {
        background: linear-gradient(135deg, #1e1b4b 0%, rgba(180, 83, 9, 0.4) 100%) !important;
        border: 2px solid #fbbf24 !important;
        box-shadow: 0 8px 30px rgba(251, 191, 36, 0.35) !important;
        padding: 20px !important;
        border-radius: 16px !important;
        text-align: center;
        margin-top: 20px;
    }
    .cal-final-title {
        font-family: 'Outfit', sans-serif;
        font-size: 1.5rem;
        font-weight: 800;
        color: #fbbf24;
        margin-bottom: 6px;
        letter-spacing: 1px;
    }
    .cal-final-desc {
        font-size: 1.25rem;
        font-weight: 700;
        color: #ffffff;
    }

    /* Mobile adjustments */
    @media (max-width: 768px) {
        .main-title { font-size: 1.5rem; }
        .sub-title { font-size: 1.05rem; }
        div[data-testid="stMetricValue"] { font-size: 1.25rem !important; }
        .stTabs [data-baseweb="tab"], .stTabs button[role="tab"] { padding: 8px 16px !important; font-size: 0.85rem !important; border-radius: 20px !important; }
        .cal-card { flex-direction: column; align-items: flex-start; gap: 6px; }
    }
</style>
""", unsafe_allow_html=True)

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

# Unified Banner: Title -> Logo (Strict Inline Sizing) -> Subtitle
logo_html = f'<img src="data:image/png;base64,{logo_b64}" style="max-width:130px !important; width:130px !important; height:auto !important; display:block; margin:8px auto 12px auto; filter:drop-shadow(0 0 12px rgba(245,158,11,0.4));" alt="Logo">' if logo_b64 else ''

st.markdown(f"""
<div class="main-header">
    <h1 class="main-title">BINGO POKER CLUB 2026</h1>
    {logo_html}
    <div class="sub-title">Liga Oficial de Poker</div>
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

# Top Metrics Row (4 Metrics: Total Rake, 50% Campeonato, 40% Mesa Final, 10% Gastos)
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.metric("💰 Rake Total", f"${int(total_rake):,}")
with c2:
    st.metric("🏆 Campeonato (50%)", f"${int(camp_total):,}")
with c3:
    st.metric("🃏 Mesa Final (40%)", f"${int(mf_total):,}")
with c4:
    st.metric("🧾 Gastos MF (10%)", f"${int(gastos_mf):,}")

# Prize Breakdown Cards (50% Campeonato, 40% Mesa Final, 10% Gastos MF)
st.markdown(f"""
<div class="prize-container">
    <div class="prize-card">
        <div class="prize-card-title">🏆 PREMIOS CAMPEONATO (50%)</div>
        <div class="prize-card-total">${int(camp_total):,}</div>
        <div class="prize-row"><span>🥇 1º Lugar (50%)</span><strong>${int(camp_total * 0.50):,}</strong></div>
        <div class="prize-row"><span>🥈 2º Lugar (30%)</span><strong>${int(camp_total * 0.30):,}</strong></div>
        <div class="prize-row"><span>🥉 3º Lugar (20%)</span><strong>${int(camp_total * 0.20):,}</strong></div>
    </div>
    <div class="prize-card">
        <div class="prize-card-title">🃏 PREMIOS MESA FINAL (40%)</div>
        <div class="prize-card-total">${int(mf_total):,}</div>
        <div class="prize-row"><span>🥇 1º Lugar (50%)</span><strong>${int(mf_total * 0.50):,}</strong></div>
        <div class="prize-row"><span>🥈 2º Lugar (30%)</span><strong>${int(mf_total * 0.30):,}</strong></div>
        <div class="prize-row"><span>🥉 3º Lugar (20%)</span><strong>${int(mf_total * 0.20):,}</strong></div>
    </div>
    <div class="prize-card">
        <div class="prize-card-title">🧾 GASTOS MESA FINAL (10%)</div>
        <div class="prize-card-total">${int(gastos_mf):,}</div>
        <div class="prize-row"><span>Fondo de Gastos Organización</span><strong>10% Rake</strong></div>
        <div class="prize-row"><span>Mantenimiento & Logística</span><strong>Acumulado</strong></div>
    </div>
</div>
""", unsafe_allow_html=True)

st.write("---")

if st.session_state["is_admin"]:
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["🏆 Posiciones", "📝 Registrar Fecha (Admin)", "💵 Rake & Pozos", "⚙️ Jugadores (Admin)", "📅 Calendario"])
else:
    tab1, tab3, tab5 = st.tabs(["🏆 Posiciones", "💵 Rake & Pozos", "📅 Calendario"])
    tab2, tab4 = None, None

with tab1:
    st.subheader("Tabla de Posiciones General")
    
    fechas_cols = FECHAS_STANDARD
    cols_display = ["Pos", "Jugador"] + fechas_cols + ["Total"]
    
    df_show = df_pos.copy()
    for col in fechas_cols:
        if col in df_show.columns:
            df_show[col] = df_show[col].apply(lambda x: int(x))
    df_show["Total"] = df_show["Total"].apply(lambda x: int(x))
    
    st.dataframe(
        df_show[cols_display],
        use_container_width=True,
        hide_index=True,
        height=340
    )
    
    st.write("---")
    st.subheader("📸 Reporte para WhatsApp")
    st.caption("Genera y descarga la imagen oficial optimizada para compartir en grupos de WhatsApp.")
    
    col_img_btn, col_img_dl = st.columns([1, 1])
    
    with col_img_btn:
        if st.button("🖼️ Generar Imagen HD para WhatsApp"):
            img_bytes = report_generator.generate_report_image(data)
            st.session_state["report_img"] = img_bytes
            st.success("¡Imagen generada con éxito!")
            
    if "report_img" in st.session_state:
        st.image(st.session_state["report_img"], caption="Reporte Oficial Bingo Poker Club 2026", use_container_width=True)
        st.download_button(
            label="📥 Descargar Imagen PNG para WhatsApp",
            data=st.session_state["report_img"],
            file_name="bingo_poker_club_posiciones.png",
            mime="image/png",
            use_container_width=True
        )

with tab3:
    st.subheader("💵 Control de Rake por Fecha")
    
    df_rake = pd.DataFrame([rake_dict])
    st.dataframe(df_rake, use_container_width=True, hide_index=True)
    
    st.subheader("🏆 Distribución de Pozos de Premios")
    df_pay = pd.DataFrame(payouts)
    st.dataframe(df_pay, use_container_width=True, hide_index=True)

with tab5:
    st.subheader("📅 Calendario Oficial de Fechas 2026 - 2027")
    st.caption("Programación de las fechas de la temporada y el Gran Evento Final.")
    
    schedule_data = [
        {"fecha": "Fecha 3", "mes": "Agosto", "desc": "Jueves 20 de agosto de 2026", "next": True},
        {"fecha": "Fecha 4", "mes": "Septiembre", "desc": "Jueves 3 de septiembre de 2026", "next": False},
        {"fecha": "Fecha 5", "mes": "Octubre", "desc": "Jueves 1 de octubre de 2026", "next": False},
        {"fecha": "Fecha 6", "mes": "Octubre", "desc": "Jueves 15 de octubre de 2026", "next": False},
        {"fecha": "Fecha 7", "mes": "Noviembre", "desc": "Jueves 5 de noviembre de 2026", "next": False},
        {"fecha": "Fecha 8", "mes": "Noviembre", "desc": "Jueves 19 de noviembre de 2026", "next": False},
        {"fecha": "Fecha 9", "mes": "Diciembre", "desc": "Jueves 3 de diciembre de 2026", "next": False},
        {"fecha": "Fecha 10", "mes": "Diciembre", "desc": "Jueves 17 de diciembre de 2026", "next": False},
    ]
    
    for s in schedule_data:
        card_class = "cal-card cal-next" if s["next"] else "cal-card"
        badge_html = '<span class="cal-badge">🔥 Próximo Torneo</span>' if s["next"] else ''
        st.markdown(f"""
        <div class="{card_class}">
            <div class="cal-num">{s['fecha']} {badge_html}</div>
            <div class="cal-desc">🗓️ {s['desc']}</div>
        </div>
        """, unsafe_allow_html=True)
        
    st.markdown("""
    <div class="cal-final">
        <div class="cal-final-title">🏆 GRAN EVENTO MESA FINAL</div>
        <div class="cal-final-desc">Sábado 09 de Enero 2027 desde las 14:00 hrs</div>
    </div>
    """, unsafe_allow_html=True)

if st.session_state["is_admin"] and tab2:
    with tab2:
        st.subheader("Ingreso de Resultados por Fecha")
        st.write("Selecciona la fecha y el tipo de torneo para asignar posiciones y calcular puntos automáticamente.")
        
        fecha_num = st.selectbox("Seleccionar Fecha", options=FECHAS_STANDARD, index=0)
        f_index = int(fecha_num) - 1
        
        tourn_type = st.selectbox(
            "Tipo de Torneo",
            options=list(data_manager.POINTS_RULES.keys()),
            index=1
        )
        
        sub_code = "FR" if "Full ring" in tourn_type else ("SH" if "Shorthanded" in tourn_type else "MM")
        if "Main Event" in tourn_type:
            sub_code = "ME-" + sub_code
            
        current_rake = rake_dict.get(f"F{int(fecha_num)}", 0)
        new_rake = st.number_input(f"Rake Recaudado en Fecha {fecha_num} ($)", min_value=0, value=int(current_rake), step=1000)
        
        st.write("#### Asignación de Posiciones (1° al 5° lugar)")
        
        all_players = df_pos["Jugador"].tolist()
        options_players = ["-- Seleccionar --"] + all_players
        
        pos1 = st.selectbox("🥇 1er Lugar", options=options_players, index=0)
        pos2 = st.selectbox("🥈 2do Lugar", options=options_players, index=0)
        pos3 = st.selectbox("🥉 3er Lugar", options=options_players, index=0)
        pos4 = st.selectbox("4to Lugar", options=options_players, index=0)
        pos5 = st.selectbox("5to Lugar", options=options_players, index=0)
        
        if st.button("💾 Guardar y Actualizar Fecha"):
            pts_rule = data_manager.POINTS_RULES[tourn_type]
            
            for idx in range(len(df_pos)):
                df_pos.at[idx, fecha_num] = 0
                
            placed = [pos1, pos2, pos3, pos4, pos5]
            for rank_idx, p_name in enumerate(placed):
                if p_name and p_name != "-- Seleccionar --":
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
            
            data_manager.save_data(df_pos, rake_dict, subheaders)
            st.success(f"¡Fecha {fecha_num} guardada exitosamente en el Excel!")
            st.rerun()

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
                    data_manager.save_data(df_pos, rake_dict, subheaders)
                    st.success(f"Jugador '{p_clean}' agregado con éxito.")
                    st.rerun()
                else:
                    st.warning("El jugador ya existe.")
