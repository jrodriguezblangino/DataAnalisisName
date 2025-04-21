
# modulo_datos.py

import pandas as pd
import warnings
warnings.filterwarnings('ignore')

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
    archivos = {
        "apellidos_provincia": "docs/apellidos_cantidad_personas_provincia_clean.csv",
        "apellidos_pais": "docs/apellidos_mas_frecuentes_pais_clean.csv",
        "apellidos_provincia_ranking": "docs/apellidos_mas_frecuentes_provincia_clean.csv",
        "historico_nombres": "docs/historico-nombres_clean.csv"
    }
    
    dataframes = {}
    for nombre, ruta in archivos.items():
        df = pd.read_csv(ruta)
        df = normalizar_columnas(df)
        dataframes[nombre] = df

    return dataframes
