import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px

# 1. Configuración de Pestaña y Estilo
st.set_page_config(
    page_title="Gold Tracker: La Ambición del Rey Enano",
    page_icon="⛏️",
    layout="wide"
)

import base64

def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

def set_png_as_page_bg(bin_file):
    bin_str = get_base64_of_bin_file(bin_file)
    page_bg_img = f'''
    <style>
    [data-testid="stAppViewContainer"] {{
        background-image: linear-gradient(rgba(14, 17, 23, 0.8), rgba(14, 17, 23, 0.8)), url("data:image/png;base64,{bin_str}");
        background-size: cover;
        background-position: center center;
        background-attachment: fixed;
    }}
    
    [data-testid="stHeader"] {{
        background: rgba(0,0,0,0);
    }}
    </style>
    '''
    st.markdown(page_bg_img, unsafe_allow_html=True)

# Aplicamos el fondo épico
try:
    set_png_as_page_bg('banner.png')
except:
    pass

# Inyectamos CSS para estética premium
st.markdown("""
    <style>
    /* Estilo General */
    .stApp {
        color: #e0e0e0;
        padding-bottom: 15vh;
    }
    
    /* Encabezado */
    .main-title {
        font-family: 'Outfit', sans-serif;
        font-weight: 800;
        color: #FFD700;
        text-align: center;
        text-shadow: 3px 3px 6px #000000;
        margin-bottom: 40px;
        letter-spacing: 2px;
    }
    
    /* Tarjetas de Métricas */
    [data-testid="stMetricValue"] {
        color: #FFD700 !important;
        font-size: 2.5rem !important;
        text-shadow: 1px 1px 2px #000;
    }
    
    /* Botones Premium */
    .stButton>button {
        background-color: rgba(31, 41, 55, 0.8);
        color: #FFD700;
        border: 2px solid #FFD700;
        border-radius: 12px;
        font-weight: bold;
        backdrop-filter: blur(5px);
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #FFD700;
        color: #000000;
        border-color: #000000;
        transform: translateY(-2px);
    }
    
    /* Pestañas */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: transparent;
    }
    .stTabs [data-baseweb="tab"] {
        height: 55px;
        background-color: rgba(31, 41, 55, 0.6);
        border-radius: 12px 12px 0px 0px;
        color: #ffffff;
        padding-left: 15px;
        padding-right: 15px;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 215, 0, 0.1);
    }
    .stTabs [aria-selected="true"] {
        background-color: rgba(255, 215, 0, 0.9) !important;
        color: #000000 !important;
        font-weight: bold;
    }

    /* Tablas y Contenedores */
    div[data-testid="stDataFrame"] {
        background-color: rgba(31, 41, 55, 0.4);
        border-radius: 15px;
        padding: 10px;
        backdrop-filter: blur(5px);
    }

    /* Adaptabilidad Móvil */
    @media (max-width: 640px) {
        .main-title {
            font-size: 1.8rem !important;
        }
        [data-testid="stMetricValue"] {
            font-size: 1.8rem !important;
        }
    }
    </style>
""", unsafe_allow_html=True)

st.markdown('<h1 class="main-title">⛏️ Gold Tracker: La Ambición del Rey Enano</h1>', unsafe_allow_html=True)

# 2. Conexión y Gestión de Datos
conn = st.connection("gsheets", type=GSheetsConnection)

def load_data():
    try:
        # Cargamos Resultados (juegos)
        results = conn.read(worksheet="juegos", ttl=0)
        # Cargamos Jugadores (jugadores)
        players_df = conn.read(worksheet="jugadores", ttl=0)
        
        # Validación y limpieza básica
        if results.empty:
            results = pd.DataFrame(columns=['fecha', 'numeroPartida', 'jugador', 'rol', 'pepitas'])
        if players_df.empty:
            players_df = pd.DataFrame(columns=['nombre'])
            
        return results, players_df
    except Exception as e:
        st.error(f"Error al conectar con Google Sheets: {e}")
        return pd.DataFrame(columns=['fecha', 'numeroPartida', 'jugador', 'rol', 'pepitas']), pd.DataFrame(columns=['nombre'])

results_df, players_df = load_data()

# Limpieza de datos inmediata para evitar errores de tipo
if not results_df.empty:
    results_df['fecha'] = pd.to_datetime(results_df['fecha'], errors='coerce', format='mixed')
    if 'numeroPartida' in results_df.columns:
        results_df['numeroPartida'] = pd.to_numeric(results_df['numeroPartida'], errors='coerce').fillna(0)
    else:
        results_df['numeroPartida'] = 0

# Aseguramos que los nombres y alias estén cargados para visualización
if not players_df.empty and 'nombre' in players_df.columns:
    # Función para crear el nombre de pantalla (Emoji + Alias/Nombre)
    def create_display_name(row):
        emoji = row['emoji'] if pd.notna(row['emoji']) else '👤'
        # Usar alias si existe, si no el nombre real
        alias = row['alias'] if pd.notna(row['alias']) and str(row['alias']).strip() != "" else row['nombre']
        return f"{emoji} {alias}"
    
    # Diccionario: Nombre Real -> Emoji + Alias
    display_name_map = dict(zip(players_df['nombre'], players_df.apply(create_display_name, axis=1)))
    # Mantenemos emoji_map para compatibilidad en otras zonas
    emoji_map = dict(zip(players_df['nombre'], players_df['emoji'].fillna('👤')))
    lista_jugadores = sorted(players_df['nombre'].tolist())
else:
    display_name_map = {}
    emoji_map = {}
    lista_jugadores = []

# 3. Navegación por Pestañas
tab_rankings, tab_game, tab_players = st.tabs(["🏆 Ranking", "⛏️ Nueva Partida", "👥 Jugadores"])

# --- TABLA DE RANKINGS ---
with tab_rankings:
    hoy = datetime.now()
    semana_actual = hoy.isocalendar()[1]
    # Lunes de esta semana
    inicio_semana = hoy - timedelta(days=hoy.weekday())
    fin_semana = inicio_semana + timedelta(days=4)
    rango_fechas = f"({inicio_semana.strftime('Lun%d')} - {fin_semana.strftime('Vie%d')})"
    
    # Cálculo de la semana pasada
    hace_7_dias = hoy - timedelta(days=7)
    semana_ant = hace_7_dias.isocalendar()[1]
    año_ant = hace_7_dias.isocalendar()[0]
    inicio_sem_ant = hace_7_dias - timedelta(days=hace_7_dias.weekday())
    fin_sem_ant = inicio_sem_ant + timedelta(days=4)
    rango_ant = f"({inicio_sem_ant.strftime('Lun%d')} - {fin_sem_ant.strftime('Vie%d')})"

    if not results_df.empty:
        # Convertimos fecha de forma flexible y calculamos semanas una sola vez
        results_df['fecha'] = pd.to_datetime(results_df['fecha'], errors='coerce', format='mixed')
        results_df = results_df.dropna(subset=['fecha'])
        results_df['semana'] = results_df['fecha'].dt.isocalendar().week
        results_df['año'] = results_df['fecha'].dt.isocalendar().year

        # 1. --- RANKING DIARIO (SOLO HOY) ---
        st.subheader(f"📍 Resultados de Hoy ({hoy.strftime('%d/%m/%Y')})")
        ranking_diario = results_df[results_df['fecha'].dt.date == hoy.date()].groupby('jugador')['pepitas'].sum().sort_values(ascending=False).reset_index()
        
        if not ranking_diario.empty:
            # Usar Alias para visualización
            ranking_diario['display_name'] = ranking_diario['jugador'].apply(lambda x: display_name_map.get(x, f"👤 {x}"))
            col_d1, col_d2 = st.columns([1, 2])
            with col_d1:
                st.metric("🏆 Líder del Día", f"{ranking_diario.iloc[0]['display_name']}", f"{ranking_diario.iloc[0]['pepitas']} 🪙")
            with col_d2:
                vista_diaria = ranking_diario[['display_name', 'pepitas']].rename(columns={'display_name': 'Jugador', 'pepitas': 'Oro Hoy'})
                st.dataframe(vista_diaria, hide_index=True, use_container_width=True)
        else:
            st.info("Aún no hay partidas registradas hoy. ¡A por ese oro! ⛏️")

        # 2. --- RANKING SEMANA ACTUAL ---
        st.divider()
        st.subheader(f"🏆 Mejores de la Semana {semana_actual} {rango_fechas}")
        ranking_semanal = results_df[
            (results_df['semana'] == semana_actual) & (results_df['año'] == hoy.isocalendar()[0])
        ].groupby('jugador')['pepitas'].sum().sort_values(ascending=False).reset_index()
        
        if not ranking_semanal.empty:
            # Usar Alias para visualización
            ranking_semanal['display_name'] = ranking_semanal['jugador'].apply(lambda x: display_name_map.get(x, f"👤 {x}"))
            c1, c2, c3 = st.columns(3)
            with c1: st.metric("🥇 1er Lugar", f"{ranking_semanal.iloc[0]['display_name']}", f"{ranking_semanal.iloc[0]['pepitas']} 🪙")
            if len(ranking_semanal) > 1:
                with c2: st.metric("🥈 2do Lugar", f"{ranking_semanal.iloc[1]['display_name']}")
            if len(ranking_semanal) > 2:
                with c3: st.metric("🥉 3er Lugar", f"{ranking_semanal.iloc[2]['display_name']}")
            
            st.divider()
            col_chart, col_table = st.columns([2, 1])
            with col_chart:
                fig = px.bar(ranking_semanal, x='display_name', y='pepitas', title="Acumulación de Oro Semanal", labels={'display_name': 'Jugador (Alias)', 'pepitas': 'Oro'}, color='pepitas', color_continuous_scale='Greens')
                fig.update_layout(template="plotly_dark", plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig, use_container_width=True)
            with col_table:
                st.markdown("**Tabla General de la Semana**")
                vista_tabla = ranking_semanal[['display_name', 'pepitas']].rename(columns={'display_name': 'Jugador', 'pepitas': 'Pepitas'})
                st.dataframe(vista_tabla, hide_index=True)
        else:
            st.info("No hay registros de la semana actual.")

        # 3. --- RANKING SEMANA ANTERIOR ---
        st.divider()
        st.subheader(f"⏮️ Ranking Semana Anterior {semana_ant} {rango_ant}")
        ranking_anterior = results_df[
            (results_df['semana'] == semana_ant) & (results_df['año'] == año_ant)
        ].groupby('jugador')['pepitas'].sum().sort_values(ascending=False).reset_index()
        
        if not ranking_anterior.empty:
            # Usar Alias para visualización
            ranking_anterior['display_name'] = ranking_anterior['jugador'].apply(lambda x: display_name_map.get(x, f"👤 {x}"))
            ca1, ca2, ca3 = st.columns(3)
            with ca1: st.metric("🥇 Ganador", f"{ranking_anterior.iloc[0]['display_name']}", f"{ranking_anterior.iloc[0]['pepitas']} 🪙")
            if len(ranking_anterior) > 1:
                with ca2: st.metric("🥈 2do", f"{ranking_anterior.iloc[1]['display_name']}")
            if len(ranking_anterior) > 2:
                with ca3: st.metric("🥉 3er", f"{ranking_anterior.iloc[2]['display_name']}")
            with st.expander("Ver tabla completa semana anterior"):
                vista_anterior = ranking_anterior[['display_name', 'pepitas']].rename(columns={'display_name': 'Jugador', 'pepitas': 'Pepitas Finales'})
                st.dataframe(vista_anterior, hide_index=True, use_container_width=True)
        else:
            st.info("No hay registros de la semana anterior.")
    else:
        st.info("Base de datos de resultados vacía.")

# --- NUEVA PARTIDA ---
with tab_game:
    st.subheader("Registrar una nueva partida")
    
    # Validación de Administrador
    acceso_admin = st.text_input("🔑 Llave de la Mina (Admin)", type="password", key="pwd_game")
    
    if acceso_admin != st.secrets.get("admin_password", "admin123"):
        st.warning("🔒 Esta sección está reservada para los Administradores de la Mina.")
    elif len(lista_jugadores) < 3:
        st.warning("Necesitas al menos 3 jugadores en la base de datos para registrar una partida.")
    else:
        # Inicializamos semillas para resetear widgets de forma segura (Key Versioning)
        if 'pepitas_seed' not in st.session_state:
            st.session_state.pepitas_seed = 0
        if 'form_seed' not in st.session_state:
            st.session_state.form_seed = 0

        col_header1, col_header2 = st.columns(2)
        with col_header1:
            fecha_juego = st.date_input("Fecha", datetime.now())
        with col_header2:
            num_jug = st.number_input("¿Cuántos jugaron hoy?", min_value=3, max_value=11, value=3)
        
        # Cálculo automático del número de partida para este día
        df_hoy = results_df[results_df['fecha'].dt.date == fecha_juego]
        if not df_hoy.empty:
            n_partida_actual = int(df_hoy['numeroPartida'].max() + 1)
        else:
            n_partida_actual = 1
            
        st.info(f"⛏️ Registrando **Partida #{n_partida_actual}** para el día {fecha_juego.strftime('%d/%m/%Y')}")
        
        st.divider()
        
        with st.form("form_partida"):
            registros_nuevos = []
            
            # Dinámicamente creamos filas para cada jugador
            for i in range(num_jug):
                st.markdown(f"**🔧 Jugador {i+1}**")
                c1, c2, c3 = st.columns([2, 2, 1])
                
                with c1:
                    # Mezclamos con form_seed para resetear nombres al guardar
                    display_list = [f"{emoji_map.get(name, '👤')} {name}" for name in lista_jugadores]
                    j_seleccionado_full = st.selectbox(
                        f"Seleccionar Jugador", 
                        display_list, 
                        key=f"sel_{i}_{st.session_state.form_seed}",
                        index=None,
                        placeholder="Elegir minero..."
                    )
                    j_nombre = j_seleccionado_full.split(" ", 1)[1] if j_seleccionado_full else None
                with c2:
                    j_rol = st.selectbox(f"Rol", ["Buscador Azul", "Buscador Verde", "Jefe", "Vago", "Geo", "Saboteador"], key=f"rol_{i}_{st.session_state.form_seed}")
                with c3:
                    # Mezclamos con pepitas_seed y form_seed para resetear puntos
                    j_pepitas = st.number_input(f"Pepitas", min_value=0, max_value=10, step=1, key=f"pts_{i}_{st.session_state.pepitas_seed}_{st.session_state.form_seed}")
                
                if j_nombre:
                    registros_nuevos.append({
                        "fecha": fecha_juego.strftime("%Y-%m-%d"),
                        "numeroPartida": n_partida_actual,
                        "jugador": j_nombre,
                        "rol": j_rol,
                        "pepitas": j_pepitas
                    })
            
            col_btns1, col_btns2 = st.columns(2)
            with col_btns1:
                submit_btn = st.form_submit_button("💾 Guardar Partida", use_container_width=True)
            with col_btns2:
                reset_btn = st.form_submit_button("🧹 Limpiar Pepitas", use_container_width=True)
            
            if reset_btn:
                # Al incrementar la semilla de pepitas, los widgets se recrean en 0
                st.session_state.pepitas_seed += 1
                st.rerun()

            if submit_btn:
                # Validar que todos los jugadores han sido seleccionados
                if len(registros_nuevos) < num_jug:
                    st.error("Por favor, selecciona a todos los jugadores antes de guardar.")
                else:
                    # Validar duplicados en la misma partida
                    j_seleccionados = [r['jugador'] for r in registros_nuevos]
                    if len(j_seleccionados) != len(set(j_seleccionados)):
                        st.error("No puedes seleccionar el mismo jugador varias veces en una partida.")
                    else:
                        new_rows = pd.DataFrame(registros_nuevos)
                        updated_results = pd.concat([results_df, new_rows], ignore_index=True)
                        conn.update(worksheet="juegos", data=updated_results)
                        
                        # Incrementamos la semilla del formulario completo para limpiar todo tras exito
                        st.session_state.form_seed += 1
                        # También reseteamos la semilla de pepitas
                        st.session_state.pepitas_seed = 0
                                
                        st.success("¡Partida registrada exitosamente!")
                        st.balloons()
                        st.cache_data.clear()
                        st.rerun()

# --- JUGADORES ---
with tab_players:
    st.subheader("Gestión de Jugadores")
    
    # Validación de Administrador
    acceso_admin_p = st.text_input("🔑 Llave de la Mina (Admin)", type="password", key="pwd_players")
    
    if acceso_admin_p != st.secrets.get("admin_password", "admin123"):
        st.warning("🔒 Solo los Capataces pueden gestionar la lista de mineros.")
    else:
        with st.form("form_nuevo_jugador", clear_on_submit=True):
            c1, c2 = st.columns(2)
            with c1:
                nuevo_nombre = st.text_input("Nombre Real (Ej: Juan)")
                nuevo_alias = st.text_input("Alias (Ej: El Minero)")
            with c2:
                opciones_emoji = ["👤", "⚒️", "💎", "👺", "⛏️", "💰", "🧱", "💣", "🔦", "🗺️", "⚖️", "👷", "🕵️", "👑", "👻", "🐺"]
                nuevo_emoji = st.selectbox("Elige tu Emoji", opciones_emoji)
            
            save_player = st.form_submit_button("➕ Añadir Jugador a la Mina")
            
            if save_player:
                if nuevo_nombre.strip() == "":
                    st.error("El nombre no puede estar vacío.")
                elif nuevo_nombre in lista_jugadores:
                    st.error("Ese jugador ya existe.")
                else:
                    new_p = pd.DataFrame([{
                        "nombre": nuevo_nombre,
                        "emoji": nuevo_emoji,
                        "alias": nuevo_alias,
                        "fechaIngreso": datetime.now().strftime("%Y-%m-%d")
                    }])
                    updated_players = pd.concat([players_df, new_p], ignore_index=True)
                    conn.update(worksheet="jugadores", data=updated_players)
                    st.success(f"¡{nuevo_nombre} ha sido añadido a la mina!")
                    st.cache_data.clear()
                    st.rerun()
        
        st.divider()
        st.markdown("**Equipo de Mineros Actual:**")
        if not players_df.empty:
            st.dataframe(players_df[['emoji', 'nombre', 'alias', 'fechaIngreso']], hide_index=True, use_container_width=True)
        else:
            st.info("Aún no hay jugadores registrados.")
        
        # --- ELIMINAR JUGADOR (ZONA DE PELIGRO) ---
        st.divider()
        with st.expander("🚨 Zona de Peligro - Eliminar Jugador"):
            if not lista_jugadores:
                st.write("No hay jugadores para eliminar.")
            else:
                with st.form("form_eliminar_jugador"):
                    jugador_a_borrar = st.selectbox("Selecciona el jugador a eliminar de la mina", lista_jugadores)
                    confirmar = st.checkbox("Confirmo que quiero eliminar a este jugador para siempre")
                    btn_borrar = st.form_submit_button("🗑️ Eliminar Definitivamente")
                    
                    if btn_borrar:
                        if not confirmar:
                            st.warning("Por favor, marca la casilla de confirmación.")
                        else:
                            # Filtramos el dataframe para quitar al jugador
                            updated_players = players_df[players_df['nombre'] != jugador_a_borrar]
                            conn.update(worksheet="jugadores", data=updated_players)
                            st.success(f"¡{jugador_a_borrar} ha sido expulsado de la mina!")
                            st.cache_data.clear()
                            st.rerun()
