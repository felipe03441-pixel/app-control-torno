import streamlit as st
import Motor

st.divider()
st.subheader("📊 Trabajos en Proceso")

df_actual = Motor.cargar_datos()

if df_actual is not None:
    df_pendientes = df_actual[df_actual['ESTADO'] == 'EN PROCESO']
    
    if not df_pendientes.empty:
        # 1. Mostramos la tabla
        st.dataframe(
            df_pendientes[['SOLICITANTE', 'PRIORIDAD', 'NOMBRE PIEZA', 'QTY', 'MATERIAL']], 
            use_container_width=True,
            hide_index=True
        )
        
        st.divider()
        st.subheader("✅ Marcar trabajo como Entregado")
        
        # 2. Creamos una lista de opciones para el menú desplegable
        # Usamos el 'index' (número de fila real en el CSV) para no equivocarnos de pieza
        opciones = []
        for indice, fila in df_pendientes.iterrows():
            texto_opcion = f"Fila {indice} - {fila['QTY']}x {fila['NOMBRE PIEZA']} ({fila['SOLICITANTE']})"
            opciones.append(texto_opcion)
            
        trabajo_seleccionado = st.selectbox("Selecciona la orden que ya fue fabricada:", opciones)
        
        # 3. Botón para actualizar
        if st.button("Confirmar Entrega", type="secondary"):
            # Extraemos el número de fila exacto del texto seleccionado
            indice_real = int(trabajo_seleccionado.split(" ")[1])
            
            # Llamamos al motor para que haga el cambio
            Motor.marcar_entregado(indice_real)
            
            st.success("¡Trabajo marcado como ENTREGADO exitosamente!")
            st.rerun() # Recarga la página automáticamente para actualizar la tabla
            
    else:
        st.success("¡Excelente! No hay trabajos pendientes en el torno.")
else:
    st.warning("No se encontró la base de datos aún.")
