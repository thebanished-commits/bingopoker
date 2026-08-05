import streamlit as st
import pandas as pd
import os
import data_manager
import report_generator

st.set_page_config(
    page_title="Bingo Poker Club 2026",
    page_icon="🏆",
    layout="wide",
    initial_sidebar_state="collapsed"
)

FECHAS_STANDARD = [f"{i:02d}" for i in range(1, 11)]

REL_LOGO = os.path.join(os.path.dirname(__file__), 'assets', 'logo.png')
ALT_LOGO_PATH = r'C:\programas\poker\logo.jpeg'

if os.path.exists(REL_LOGO):
    LOGO_PATH = REL_LOGO
elif os.path.exists(ALT_LOGO_PATH):
    LOGO_PATH = ALT_LOGO_PATH
else:
    LOGO_PATH = None

ADMIN_PASSWORD = "admin"

if "is_admin" not in st.session_state:
    st.session_state["is_admin"] = False

# Custom Mobile-First CSS Styling
st.markdown("""
<style>
    /* Dark / Gold Modern Theme */
    .stApp {
        background-color: #0b1320;
        color: #e2e8f0;
    }
    
    /* Header Container */
    .main-header {
        background: linear-gradient(135deg, #1b365d 0%, #0f223d 100%);
        padding: 1.2rem;
        border-radius: 12px;
        text-align: center;
        margin-bottom: 1rem;
        border: 1px solid #2b4c7e;
        box-shadow: 0 4px 15px rgba(0,0,0,0.4);
    }
    .main-title {
        color: #facc15;
        font-family: 'Arial', sans-serif;
        font-weight: 800;
        font-size: 1.8rem;
        margin: 0;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .sub-title {
        color: #94a3b8;
        font-size: 0.95rem;
        margin-top: 4px;
    }
    
    /* Center Logo Image */
    .logo-container {
        display: flex;
        justify-content: center;
        margin-bottom: 0.5rem;
    }
    
    /* Metric Cards */
    div[data-testid="stMetricValue"] {
        font-size: 1.5rem !important;
        color: #facc15 !important;
        font-weight: 700;
    }
    div[data-testid="stMetric"] {
        background-color: #162238;
        border: 1px solid #283a5a;
        padding: 12px;
        border-radius: 10px;
    }
    
    /* Buttons */
    .stButton>button {
        width: 100%;
        background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
        color: white;
        font-weight: 700;
        border: none;
        border-radius: 8px;
        padding: 0.6rem 1rem;
        font-size: 1rem;
        transition: all 0.2s ease;
    }
    .stButton>button:hover {
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
        transform: translateY(-1px);
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 6px;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 10px 16px;
        background-color: #162238;
        border-radius: 8px 8px 0 0;
        color: #cbd5e1;
        font-weight: 600;
    }
    .stTabs [aria-selected="true"] {
        background-color: #2563eb !important;
        color: white !important;
    }

    /* Mobile adjustments */
    @media (max-width: 768px) {
        .main-title { font-size: 1.4rem; }
        div[data-testid="stMetricValue"] { font-size: 1.2rem !important; }
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

# Centered Logo above title banner
if LOGO_PATH and os.path.exists(LOGO_PATH):
    col_l1, col_l2, col_l3 = st.columns([1, 1, 1])
    with col_l2:
        st.image(LOGO_PATH, width=150)

st.markdown("""
<div class="main-header">
    <h1 class="main-title">BINGO POKER CLUB 2026</h1>
    <div class="sub-title">Liga Oficial de Poker - Gestión de Posiciones y Rake</div>
</div>
""", unsafe_allow_html=True)

data = data_manager.load_data()
df_pos = data["df_posiciones"]
rake_dict = data["rake_dict"]
total_rake = data["total_rake"]
payouts = data["payouts"]
subheaders = data["subheaders"]

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.metric("💰 Rake Total", f"${int(total_rake):,}")
with c2:
    st.metric("🏆 Campeonato (60%)", f"${int(total_rake * 0.60):,}")
with c3:
    st.metric("🃏 Mesa Final (40%)", f"${int(total_rake * 0.40):,}")
with c4:
    lider = df_pos.iloc[0]["Jugador"] if not df_pos.empty else "N/A"
    st.metric("🥇 Líder Actual", lider)

st.write("---")

if st.session_state["is_admin"]:
    tab1, tab2, tab3, tab4 = st.tabs(["🏆 Posiciones", "📝 Registrar Fecha (Admin)", "💵 Rake & Pozos", "⚙️ Jugadores (Admin)"])
else:
    tab1, tab3 = st.tabs(["🏆 Posiciones", "💵 Rake & Pozos"])
    tab2, tab4 = None, None
    st.info("ℹ️ Estás en **Modo Visualización (Lectura)**. Para agregar resultados o administrar la liga, abre el menú lateral e ingresa con la clave de administrador.")

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
