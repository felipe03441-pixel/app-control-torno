import streamlit as st
import pandas as pd
import plotly.express as px
import Motor

# --- CONFIGURACIÓN DE PÁGINA Y TEMA ---
st.set_page_config(page_title="Sistema Torno CNC", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
    .stApp { background-color: #1e1e2e; color: #cdd6f4; }
    .stSidebar { background-color: #313244; border-right: 1px solid #45475a; }
    h1, h2, h3 { color: #89b4fa!important; }
</style>
""", unsafe_allow_html=True)

# --- CARGA DE DATOS ---
df_original, df_actual = Motor.cargar_datos()

if df_actual is None:
    st.error("❌ No se pudo cargar la base de datos. Verifica la carpeta 'datos'.")
    st.stop()

# Asegurar que la columna ESTADO existe
if 'ESTADO' not in df_actual.columns:
    df_actual['ESTADO'] = 'EN PROCESO'

# --- MENÚ LATERAL (SIDEBAR) ---
st.sidebar.title("⚙️ Menú Principal")
menu = st.sidebar.radio("Navegación", [
    "📊 Dashboard Analytics", 
    "📝 Nueva Orden de Trabajo", 
    "✅ Control de Entregas"
])
st.sidebar.divider()
st.sidebar.info("Sistema Integral de Producción y Mantenimiento - Torno")

# ==========================================
# 1. PANTALLA: DASHBOARD ANALYTICS
# ==========================================
if menu == "📊 Dashboard Analytics":
    st.title("📊 Dashboard de Producción CNC")
    
    # Filtro superior
    sedes = ["Todas"] + list(df_actual['SOLICITANTE'].unique())
    sede_sel = st.selectbox("Filtrar por Sede:", sedes)
    
    df_filtrado = df_actual if sede_sel == "Todas" else df_actual[df_actual['SOLICITANTE'] == sede_sel]
    
    # KPIs
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Piezas Solicitadas", int(df_filtrado['QTY'].sum()))
    with col2:
        en_proceso = len(df_filtrado[df_filtrado['ESTADO'] == 'EN PROCESO'])
        st.metric("Órdenes en Proceso", en_proceso)
    with col3:
        if 'TIEMPO DEMORADO (DÍAS)' in df_filtrado.columns:
            # Filtramos solo los entregados para calcular el promedio real
            entregados = df_filtrado[df_filtrado['ESTADO'] == 'ENTREGADO']
            tiempo_promedio = pd.to_numeric(entregados['TIEMPO DEMORADO (DÍAS)'], errors='coerce').mean()
            tiempo_mostrar = f"{tiempo_promedio:.1f} días" if not pd.isna(tiempo_promedio) else "N/A"
            st.metric("Tiempo Prom. Entrega", tiempo_mostrar)
            
    st.divider()
    
    # Gráficas
    col_graf1, col_graf2 = st.columns(2)
    
    with col_graf1:
        st.subheader("Estado de Órdenes")
        estado_counts = df_filtrado['ESTADO'].value_counts().reset_index()
        estado_counts.columns = ['ESTADO', 'CANTIDAD']
        fig1 = px.pie(estado_counts, values='CANTIDAD', names='ESTADO', hole=0.4, 
                      color='ESTADO', color_discrete_map={'ENTREGADO':'#a6e3a1', 'EN PROCESO':'#fab387'})
        fig1.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color='#cdd6f4')
        st.plotly_chart(fig1, use_container_width=True)
        
    with col_graf2:
        st.subheader("Materiales Más Solicitados")
        mat_counts = df_filtrado.groupby('MATERIAL')['QTY'].sum().reset_index()
        fig2 = px.bar(mat_counts, x='MATERIAL', y='QTY', color='MATERIAL')
        fig2.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color='#cdd6f4')
        st.plotly_chart(fig2, use_container_width=True)

# ==========================================
# 2. PANTALLA: NUEVA ORDEN DE TRABAJO
# ==========================================
elif menu == "📝 Nueva Orden de Trabajo":
    st.title("📝 Registrar Nueva Orden")
    st.write("Completa el formulario para ingresar un nuevo trabajo al taller.")
    
    with st.form("form_nueva_orden", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            solicitante = st.text_input("Sede Solicitante (Ej. Bodytech Kennedy)")
            pieza = st.text_input("Nombre de la Pieza")
            cantidad = st.number_input("Cantidad (QTY)", min_value=1, step=1)
        with col2:
            prioridad = st.selectbox("Prioridad", ["BAJA (MP)", "MEDIA (FL)", "ALTA (FS)"])
            material = st.selectbox("Material", ["ACERO", "ACERO PLATA", "ALUMINIO", "BRONCE", "ACERO PLATA Y ALUMINIO", "POR DEFINIR"])
            dimensiones = st.text_input("Dimensiones (Opcional)", value="SEGUN MUESTRA")
            
        btn_guardar = st.form_submit_button("➕ Guardar Orden en Sistema")
        
        if btn_guardar:
            if solicitante == "" or pieza == "":
                st.error("⚠️ La Sede y el Nombre de la Pieza son obligatorios.")
            else:
                # Llamamos a Motor.py
                Motor.agregar_solicitud(solicitante, prioridad, pieza, material, cantidad, dimensiones)
                st.success(f"✅ ¡Orden creada exitosamente para {solicitante}! Ya aparece 'EN PROCESO'.")

# ==========================================
# 3. PANTALLA: CONTROL DE ENTREGAS
# ==========================================
elif menu == "✅ Control de Entregas":
    st.title("✅ Control de Producción y Entregas")
    
    df_pendientes = df_actual[df_actual['ESTADO'] == 'EN PROCESO']
    
    if not df_pendientes.empty:
        st.write("### 🛠️ Trabajos Activos en Taller:")
        st.dataframe(
            df_pendientes[['SOLICITANTE', 'PRIORIDAD', 'NOMBRE PIEZA', 'QTY', 'MATERIAL', 'FECHA SOLICITUD']], 
            use_container_width=True, hide_index=False
        )
        
        st.divider()
        st.subheader("Marcar trabajo como Terminado")
        
        opciones = []
        for indice, fila in df_pendientes.iterrows():
            texto_opcion = f"Índice {indice} | {fila['QTY']}x {fila['NOMBRE PIEZA']} - {fila['SOLICITANTE']}"
            opciones.append(texto_opcion)
            
        col_sel, col_btn = st.columns([3, 1])
        with col_sel:
            trabajo_seleccionado = st.selectbox("Selecciona el trabajo finalizado:", opciones)
        with col_btn:
            st.write("") # Espaciado
            st.write("") # Espaciado
            if st.button("Confirmar Entrega 🚀", use_container_width=True):
                # Extraemos el número de índice del texto
                indice_real = int(trabajo_seleccionado.split(" ")[1])
                Motor.marcar_entregado(indice_real)
                st.success("¡Pieza entregada con éxito! Remisión generada.")
                st.rerun()
    else:
        st.success("🎉 ¡Excelente trabajo! El taller no tiene órdenes pendientes. Todo está entregado.")
        
    with st.expander("Ver Histórico de Piezas Entregadas"):
        st.dataframe(df_actual[df_actual['ESTADO'] == 'ENTREGADO'], use_container_width=True)