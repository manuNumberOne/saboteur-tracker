import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Pico y Datos", page_icon="⛏️")

st.title("⛏️ Pico y Datos: Saboteur Tracker")

# 1. Conexión y Limpieza de Datos
conn = st.connection("gsheets", type=GSheetsConnection)
df = conn.read(ttl=0)

# Normalizamos nombres de columnas para evitar el error anterior
if not df.empty:
    df.columns = [c.strip().lower() for c in df.columns]
else:
    df = pd.DataFrame(columns=['fecha', 'jugador', 'rol', 'pepitas'])

# 2. Gestión de Jugadores (Base existente + nuevos)
jugadores_habituales = ["Manu", "Emilia"] # Puedes agregar más fijos aquí
if not df.empty:
    jugadores_en_bd = df['jugador'].unique().tolist()
    lista_jugadores = list(set(jugadores_habituales + jugadores_en_bd))
else:
    lista_jugadores = jugadores_habituales

# 3. Interfaz de Entrada de Partida
with st.form("nueva_partida"):
    st.subheader("Registrar Partida")
    
    col1, col2 = st.columns(2)
    with col1:
        fecha = st.date_input("Día", datetime.now())
    with col2:
        n_partida = st.number_input("N° de Partida", min_value=1, step=1)
    
    num_jugadores = st.slider("¿Cuántos jugaron?", 2, 10, 3)
    
    registros_partida = []
    
    st.divider()
    
    # Generamos campos dinámicos según el número de jugadores seleccionado
    for i in range(num_jugadores):
        st.markdown(f"**Jugador {i+1}**")
        c1, c2, c3 = st.columns([2, 2, 1])
        
        with c1:
            modo_jugador = st.radio(f"Tipo J{i+1}", ["Existente", "Nuevo"], key=f"mode_{i}", horizontal=True)
            if modo_jugador == "Existente":
                nombre = st.selectbox(f"Nombre J{i+1}", lista_jugadores, key=f"select_{i}")
            else:
                nombre = st.text_input(f"Escribir J{i+1}", key=f"text_{i}")
        
        with c2:
            rol = st.selectbox(f"Rol J{i+1}", ["Buscador", "Saboteador", "Perezoso", "Geólogo", "Aprovechado"], key=f"rol_{i}")
        
        with c3:
            puntos = st.number_input(f"Pepitas", min_value=0, max_value=10, step=1, key=f"puntos_{i}")
        
        if nombre:
            registros_partida.append({
                "fecha": fecha.strftime("%Y-%m-%d"),
                "jugador": nombre,
                "rol": rol,
                "pepitas": puntos
            })

    submit = st.form_submit_button("💾 Guardar Resultados de la Partida")

    if submit:
        if len(registros_partida) > 0:
            new_data = pd.DataFrame(registros_partida)
            updated_df = pd.concat([df, new_data], ignore_index=True)
            conn.update(data=updated_df)
            st.success(f"¡Partida {n_partida} registrada exitosamente!")
            st.rerun()
        else:
            st.error("Faltan datos de jugadores.")

# 4. Ranking Semanal
st.divider()
st.subheader("🏆 Ranking de la Semana")

if not df.empty and 'fecha' in df.columns:
    df['fecha'] = pd.to_datetime(df['fecha'])
    # Calcular semana actual
    semana_actual = datetime.now().isocalendar()[1]
    df['semana'] = df['fecha'].dt.isocalendar().week
    
    ranking = df[df['semana'] == semana_actual].groupby('jugador')['pepitas'].sum().sort_values(ascending=False).reset_index()
    
    if not ranking.empty:
        st.dataframe(ranking, hide_index=True, use_container_width=True)
    else:
        st.info("No hay datos para esta semana todavía.")
