# modulo_datos.py

import pandas as pd
import os
import warnings
warnings.filterwarnings('ignore')

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DOCS_DIR = os.path.join(BASE_DIR, 'docs')

# Función para normalizar nombres de columnas
def normalizar_columnas(df):
    df.columns = [col.replace('"', '').strip() for col in df.columns]
    return df

# Función para buscar variantes con y sin tilde
def buscar_variantes(df, columna, valor):
    resultado = df[df[columna] == valor]
    if len(resultado) == 0:
        if 'í' in valor:
            resultado = df[df[columna] == valor.replace('í', 'i')]
        elif 'i' in valor:
            resultado = df[df[columna] == valor.replace('i', 'í')]
        elif 'ó' in valor:
            resultado = df[df[columna] == valor.replace('ó', 'o')]
        elif 'o' in valor:
            resultado = df[df[columna] == valor.replace('o', 'ó')]
    return resultado

# Función principal para cargar los datasets ya limpiados
def cargar_datasets():
    rutas = {
        'apellidos_provincia': os.path.join(DOCS_DIR, 'apellidos_cantidad_personas_provincia_clean.csv'),
        'apellidos_pais': os.path.join(DOCS_DIR, 'apellidos_mas_frecuentes_pais_clean.csv'),
        'apellidos_mas_frecuentes_provincia': os.path.join(DOCS_DIR, 'apellidos_mas_frecuentes_provincia_clean.csv'),
        'historico_nombres': os.path.join(DOCS_DIR, 'historico-nombres_clean.csv'),
    }

    dataframes = {}  # Inicializamos el diccionario 'dataframes'

    # Verificar si los archivos existen y leerlos
    for clave, ruta in rutas.items():
        print(f"Leyendo archivo: {ruta}")
        if not os.path.exists(ruta):
            raise FileNotFoundError(f"No se encontró el archivo: {ruta}")
        dataframes[clave] = pd.read_csv(ruta)

    return dataframes

if __name__ == "__main__":
    datos = cargar_datasets()
    print(f"Archivos cargados: {list(datos.keys())}")
