import pandas as pd
import re
from io import StringIO
from collections import defaultdict

# ---------- UTILIDADES ----------

def leer_csv_con_reemplazo(path):
    """
    Lee un archivo CSV y reemplaza caracteres no válidos.

    Args:
        path (str): Ruta del archivo CSV a leer.

    Returns:
        pd.DataFrame: DataFrame con el contenido del CSV, o None si hay un error.
    """
    try:
        with open(path, encoding='utf-8', errors='replace') as f:
            contenido = f.read()  # Lee el contenido del archivo
        return pd.read_csv(StringIO(contenido))  # Carga el contenido en un DataFrame
    except Exception as e:
        print(f"Error leyendo {path}: {e}")  # Manejo de errores
        return None

def extraer_contexto(texto, char, ventana=10):
    """
    Extrae contextos alrededor de un carácter específico en un texto.

    Args:
        texto (str): Texto del cual extraer contextos.
        char (str): Carácter alrededor del cual se extraerá el contexto.
        ventana (int): Número de caracteres a incluir antes y después del carácter.

    Returns:
        list: Lista de contextos extraídos.
    """
    posiciones = [m.start() for m in re.finditer(re.escape(char), texto)]  # Encuentra posiciones del carácter
    contextos = []
    for pos in posiciones:
        inicio = max(pos - ventana, 0)  # Calcula el inicio del contexto
        fin = min(pos + ventana + 1, len(texto))  # Calcula el fin del contexto
        contexto = texto[inicio:fin].replace('\n', ' ').strip()  # Extrae y limpia el contexto
        contextos.append(contexto)  # Agrega el contexto a la lista
    return contextos

def recolectar_contextos(df, caracteres_sospechosos, max_ejemplos=3):
    """
    Recolecta contextos de un DataFrame para caracteres sospechosos.

    Args:
        df (pd.DataFrame): DataFrame del cual recolectar contextos.
        caracteres_sospechosos (set): Conjunto de caracteres a buscar en el DataFrame.
        max_ejemplos (int): Número máximo de ejemplos a recolectar por carácter.

    Returns:
        dict: Diccionario con contextos recolectados.
    """
    contextos = defaultdict(lambda: defaultdict(set))  # Estructura para almacenar contextos
    for col in df.select_dtypes(include='object').columns:  # Itera sobre columnas de tipo objeto
        for valor in df[col].dropna():  # Itera sobre valores no nulos
            if not isinstance(valor, str):
                continue  # Solo procesa cadenas
            for char in caracteres_sospechosos:
                if char in valor and len(contextos[col][char]) < max_ejemplos:
                    ejemplos = extraer_contexto(valor, char)  # Extrae contextos
                    for ej in ejemplos:
                        if len(contextos[col][char]) < max_ejemplos:
                            contextos[col][char].add(ej)  # Agrega el contexto al diccionario
    return contextos

# ---------- ARCHIVOS A ANALIZAR ----------


archivos = {
    "apellidos_provincia": "docs/apellidos_cantidad_personas_provincia.csv",
    "apellidos_pais": "docs/apellidos_mas_frecuentes_pais.csv",
    "apellidos_provincia_ranking": "docs/apellidos_mas_frecuentes_provincia.csv",
    "historico-nombres": "docs/historico-nombres.csv"
}

# ---------- PROCESAMIENTO CON CONTEXTO ----------

reporte_completo = {}  # Diccionario para almacenar el reporte final

for nombre_logico, ruta in archivos.items():
    print(f"\n📄 Procesando {ruta}...")  
    df = leer_csv_con_reemplazo(ruta) 
    if df is not None:
        caracteres = set()  # Conjunto para almacenar caracteres sospechosos
        for col in df.select_dtypes(include='object').columns:  # Itera sobre columnas de tipo objeto
            for val in df[col].dropna():  # Itera sobre valores no nulos
                if isinstance(val, str):
                    encontrados = re.findall(r'[^\x00-\x7F]', val)  # Busca caracteres no ASCII
                    caracteres.update(encontrados)  # Agrega caracteres encontrados al conjunto
        contextos = recolectar_contextos(df, caracteres)  # Recolecta contextos
        reporte_completo[nombre_logico] = contextos  # Almacena contextos en el reporte
    else:
        print(f"⚠️ No se pudo procesar {ruta}.")  # Mensaje de error si no se pudo leer el archivo

# ---------- GUARDAR REPORTE DE CONTEXTOS ----------

with open("docs/reporte_contextos.txt", "w", encoding="utf-8") as f:
    for archivo, columnas in reporte_completo.items():
        f.write(f"\n=== Archivo: {archivo} ===\n")  # Escribe el nombre del archivo
        for columna, chars in columnas.items():
            f.write(f"\nColumna: {columna}\n")  # Escribe el nombre de la columna
            for char, ejemplos in chars.items():
                f.write(f"\n  Carácter: {repr(char)}\n")  # Escribe el carácter sospechoso
                for ej in ejemplos:
                    f.write(f"    -> {ej}\n")  # Escribe los ejemplos de contexto

print("\n✅ Contextos guardados en 'reporte_contextos.txt'. Revisá los ejemplos para decidir qué reemplazar.")
