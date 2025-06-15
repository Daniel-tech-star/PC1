
import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="Autoevaluación de Carrera", layout="wide")

st.title("Formulario de Autoevaluación de Carrera")
st.markdown("Completa los siguientes campos para evaluar tus competencias y comportamientos.")

# Cargar datos base
@st.cache_data
def cargar_datos_base():
    df_comp = pd.read_excel("Valoracion_Jobs.xlsx", sheet_name="Competencias")
    df_beh = pd.read_excel("Valoracion_Jobs.xlsx", sheet_name="Comportamientos")
    return df_comp, df_beh

df_comp, df_beh = cargar_datos_base()

# Obtener áreas y puestos
areas = df_comp["Area"].dropna().unique().tolist()
selected_area = st.selectbox("Selecciona tu área actual", sorted(areas))
puestos = df_comp[df_comp["Area"] == selected_area]["Job Title"].unique().tolist()
selected_puesto = st.selectbox("Selecciona tu puesto actual", sorted(puestos))
nombre = st.text_input("Nombre completo")

# Evaluación de competencias
st.subheader("1. Competencias (reparte 100 puntos entre todas)")
competencias = df_comp.columns[3:11].tolist()
competencias_vals = {}
total = 0
cols = st.columns(4)
for i, comp in enumerate(competencias):
    with cols[i % 4]:
        val = st.number_input(comp, min_value=0, max_value=100, step=1, key=comp)
        competencias_vals[comp] = val
        total += val
st.write(f"**Total asignado:** {total} / 100")

# Evaluación de comportamientos agrupados por competencia
st.subheader("2. Comportamientos por competencia (1 = Nunca, 5 = Muy frecuentemente)")
beh_vals = {}
for comp in competencias:
    st.markdown(f"**{comp}**")
    items = df_beh[df_beh["Competencias"] == comp]["Comportamientos"].dropna().tolist()
    for i, item in enumerate(items):
        clean_item = item.split(".", 1)[-1].strip()
        beh_vals[clean_item] = st.slider(clean_item, 1, 5, 3, key=f"{comp}_{i}")

# Validación final y guardar
if st.button("Enviar autoevaluación"):
    if total != 100:
        st.error("Debes asignar exactamente 100 puntos entre las competencias.")
    elif not nombre or not selected_area or not selected_puesto:
        st.error("Por favor, completa todos los campos.")
    else:
        data = {
            "Nombre": nombre,
            "Puesto": selected_puesto,
            "Area": selected_area,
            **competencias_vals,
            **{f"{k} (comportamiento)": v for k, v in beh_vals.items()}
        }
        df = pd.DataFrame([data])
        filename = f"autoevaluacion_{nombre.replace(' ', '_')}.xlsx"
        df.to_excel(filename, index=False)
        st.success(f"Autoevaluación guardada como {filename}")
        st.download_button("Descargar autoevaluación", data=open(filename, "rb"), file_name=filename, mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
