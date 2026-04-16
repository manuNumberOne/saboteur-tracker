import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Saboteur Admin", page_icon="🏆")

st.title("🏆 Saboteur: Conteo de Pepitas")

# Conexión a Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# Leer datos existentes
df = conn.read(ttl=0) # ttl=0 para que no use caché y lea siempre lo último

# --- INTERFAZ DE ENTRADA ---
with st.expander("📝 Registrar Nueva Partida"):
    with st.form("entry_form"):
        fecha = st.date_input("Fecha", datetime.now())
        jugador = st.selectbox("Jugador", ["Manu", "Emilia", "Jugador 3", "Jugador 4"])
        rol = st.selectbox("Rol", ["Buscador", "Saboteador", "Perezoso", "Geólogo", "Aprovechado"])
        pepitas = st.number_input("Pepitas Ganadas", min_value=0, max_value=10, step=1)
        
        submit = st.form_submit_button("Guardar Resultado")

        if submit:
            new_row = pd.DataFrame([{
                "Fecha": fecha.strftime("%Y-%m-%d"),
                "Jugador": jugador,
                "Rol": rol,
                "Pepitas": pepitas
            }])
            # Concatenar y actualizar
            updated_df = pd.concat([df, new_row], ignore_index=True)
            conn.update(data=updated_df)
            st.success(f"¡Puntos registrados para {jugador}!")
            st.rerun()

# --- RANKING SEMANAL ---
st.subheader("📊 Ranking de la Semana")

if not df.empty:
    df['Fecha'] = pd.to_datetime(df['Fecha'])
    # Calcular inicio de semana (Lunes)
    df['Semana'] = df['Fecha'].dt.isocalendar().week
    current_week = datetime.now().isocalendar()[1]
    
    # Filtrar y Agrupar
    ranking_semanal = df[df['Semana'] == current_week].groupby('Jugador')['Pepitas'].sum().sort_values(ascending=False).reset_index()
    
    # Mostrar Ranking con estilo
    st.table(ranking_semanal)
else:
    st.info("Aún no hay datos registrados.")
