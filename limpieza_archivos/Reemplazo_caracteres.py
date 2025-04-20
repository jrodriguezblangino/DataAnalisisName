import pandas as pd
import os
import re

# Diccionarios de reemplazo por archivo
REEMPLAZOS = {
    'apellidos_provincia': {
        'ò': 'ó', 'û': 'ü', 'ù': 'ú', 'è': 'é', 'ì': 'í'
    },
    'historico_nombres': {
        'è': 'é', 'Ú': 'ú', 'É': 'é', 'à': 'á', 'ù': 'ú', 'ò': 'ó',
        'ì': 'í', 'Ñ': 'ñ', 'Í': 'í', 'ô': 'ó', '¤': 'ñ', 'Ó': 'ó',
        'È': 'é', 'Ü': 'ü', 'Ì': 'í', 'Ù': 'ú', 'Ò': 'ó', 'î': 'í',
        'ê': 'é', 'û': 'ú', 'Ç': 'ç', 'ý': 'í', 'À': 'á', 'µ': 'a',
        'Ô': 'ó', '¡': 'i', 'Î': 'í', '£´': 'ú', 'Ä': 'á', '¢': 'ó',
        '\xa0': 'á', '\x93': 'í', 'Ê': 'e', '¨': ' ', '\x90': 'é',
        'ÿ': 'i', 'ć': 'ó', 'ẽ': 'é', '¿': '', 'Û': 'ü', 'Ŷ': 'i',
        'Å': 'á', '\x82': ''
    }
}

# Mapear nombres reales a nombres lógicos
ARCHIVOS = {
    "apellidos_provincia": "docs/apellidos_cantidad_personas_provincia.csv",
    "apellidos_pais": "docs/apellidos_mas_frecuentes_pais.csv",
    "apellidos_provincia_ranking": "docs/apellidos_mas_frecuentes_provincia.csv",
    "historico-nombres": "docs/historico-nombres.csv"
}

# Función de corrección según archivo
def corregir_texto(texto, reemplazos):
    if not isinstance(texto, str):
        return texto
    for mal, bien in reemplazos.items():
        texto = texto.replace(mal, bien)
    return texto

# Cargar, limpiar y guardar dataset
def limpiar_archivo(nombre_logico, ruta_archivo, encoding='utf-8'):
    print(f"Procesando: {ruta_archivo}")
    try:
        df = pd.read_csv(ruta_archivo, encoding=encoding)
    except UnicodeDecodeError:
        df = pd.read_csv(ruta_archivo, encoding='latin1')
    
    reemplazos = REEMPLAZOS.get(nombre_logico, {})

    if reemplazos:
        for columna in df.select_dtypes(include=['object']).columns:
            df[columna] = df[columna].apply(lambda x: corregir_texto(x, reemplazos))

    # Normalizar nombres de columnas
    df.columns = [col.replace('"', '') for col in df.columns]

    # Guardar CSV limpio
    output_name = ruta_archivo.replace('.csv', '_clean.csv')
    df.to_csv(output_name, index=False)
    print(f"Guardado: {output_name}\n")

    return df

# Procesar todos los archivos
dataframes_limpios = {}
for nombre_logico, ruta_archivo in ARCHIVOS.items():
    df = limpiar_archivo(nombre_logico, ruta_archivo)
    dataframes_limpios[nombre_logico] = df
