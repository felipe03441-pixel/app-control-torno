# --- SECCIÓN DE VISUALIZACIÓN Y ACTUALIZACIÓN ---
st.divider()
st.subheader("📊 Trabajos en Proceso")

df_actual = motor.cargar_datos()

# ESTE ES EL CÓDIGO QUE NOS DIRÁ QUÉ ESTÁ PASANDO:
if df_actual is not None:
    st.write(f"DEBUG: Se encontraron {len(df_actual)} filas en la base de datos.") # Esto nos dirá si lee algo
    
    # Filtramos la tabla para mostrar SOLO lo que está 'EN PROCESO'
    df_pendientes = df_actual[df_actual['ESTADO'] == 'EN PROCESO']
    
    if not df_pendientes.empty:
        st.dataframe(df_pendientes, use_container_width=True)
    else:
        st.info("No hay trabajos pendientes en el torno.")
else:
    st.error("No se pudo cargar el archivo CSV. Revisa la ruta de la carpeta 'datos'.")
