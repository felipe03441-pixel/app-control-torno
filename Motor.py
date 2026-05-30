import pandas as pd
import os
from datetime import datetime 

ARCHIVO_DATOS = 'datos/control_solicitudes torno.csv'

def cargar_datos():
    if os.path.exists(ARCHIVO_DATOS):
        return pd.read_csv(ARCHIVO_DATOS)
    return None

def resumen_produccion():
    df = cargar_datos()
    if df is not None:
        print(f"\n--- RESUMEN DEL TORNO ---")
        print(f"Total de solicitudes: {len(df)}")
        print(df['ESTADO'].value_counts().to_string())

# --- ¡AGREGA ESTA NUEVA FUNCIÓN! ---
def agregar_solicitud(solicitante, prioridad, nombre_pieza, material, cantidad):
    """Crea una nueva orden de trabajo y la guarda en el CSV."""
    df = cargar_datos()
    
    if df is not None:
        # Creamos la nueva fila con los datos ingresados
        nueva_fila = pd.DataFrame([{
            'SOLICITANTE': solicitante,
            'PRIORIDAD': prioridad,
            'NOMBRE PIEZA': nombre_pieza,
            'MATERIAL': material,
            'QTY': cantidad,
            'ESTADO': 'EN PROCESO' # Por defecto entra en proceso
        }])
        
        # Unimos la nueva fila al archivo existente y lo guardamos
        df = pd.concat([df, nueva_fila], ignore_index=True)
        df.to_csv(ARCHIVO_DATOS, index=False)
        print("\n✅ ¡Orden de trabajo guardada exitosamente en el sistema!")


def marcar_entregado(indice_fila):
    """Cambia el estado de una pieza a ENTREGADO y anota la fecha actual."""
    df = cargar_datos()
    if df is not None:
        # Cambiamos el estado
        df.at[indice_fila, 'ESTADO'] = 'ENTREGADO'
        
        # Anotamos la fecha de hoy automáticamente
        fecha_hoy = datetime.now().strftime("%d/%m/%Y")
        df.at[indice_fila, 'FECHA ENTREGA'] = fecha_hoy
        
        # Guardamos el archivo actualizado
        df.to_csv(ARCHIVO_DATOS, index=False)