import pandas as pd
import re
from io import StringIO

# ---------- FUNCIONES BASE ----------

def leer_csv_con_reemplazo(path: str) -> pd.DataFrame:
    """
    Lectura del archivo CSV y reemplazo de caracteres no válidos.

    Args:
        path (str): Ruta del archivo CSV a leer.

    Returns:
        pd.DataFrame: DataFrame con el contenido del CSV, o None si hay un error.
    """
    try:
        # Abre el archivo CSV con codificación UTF-8 y reemplaza errores de codificación.
        with open(path, encoding='utf-8', errors='replace') as f:
            contenido = f.read()
        # Lee el contenido del archivo CSV en un DataFrame de pandas.
        return pd.read_csv(StringIO(contenido))
    except Exception as e:
        # Captura cualquier excepción y muestra un mensaje de error.
        print(f"Error leyendo {path}: {e}")
        return None

def detectar_caracteres_invalidos(texto: str) -> set:
    """
    Detecta caracteres no ASCII en un texto.

    Args:
        texto (str): Texto en el que se buscarán caracteres no válidos.

    Returns:
        set: Conjunto de caracteres no válidos encontrados en el texto.
    """
    if not isinstance(texto, str):
        return set()
    # Define un patrón para encontrar caracteres no ASCII.
    patron = re.compile(r'[^\x00-\x7F]+')
    return set(patron.findall(texto))

def analizar_caracteres_invalidos(df: pd.DataFrame) -> set:
    """
    Analiza un DataFrame para detectar caracteres no válidos en columnas de tipo objeto.

    Args:
        df (pd.DataFrame): DataFrame a analizar.

    Returns:
        set: Conjunto de caracteres sospechosos encontrados en el DataFrame.
    """
    caracteres_sospechosos = set()
    # Itera sobre las columnas de tipo objeto en el DataFrame.
    for columna in df.select_dtypes(include='object').columns:
        # Itera sobre los valores de la columna, ignorando los valores nulos.
        for valor in df[columna].dropna():
            # Actualiza el conjunto de caracteres sospechosos con los encontrados en el valor.
            caracteres_sospechosos.update(detectar_caracteres_invalidos(valor))
    return caracteres_sospechosos

# ---------- PROCESO PARA TODOS LOS ARCHIVOS ----------

# Diccionario que mapea nombres lógicos a rutas de archivos CSV.
archivos = {
    "apellidos_provincia": "docs/apellidos_cantidad_personas_provincia.csv",
    "apellidos_pais": "docs/apellidos_mas_frecuentes_pais.csv",
    "apellidos_provincia_ranking": "docs/apellidos_mas_frecuentes_provincia.csv",
    "historico-nombres": "docs/historico-nombres.csv"
}

# Diccionario para almacenar los reportes de caracteres sospechosos.
reportes = {}

# Itera sobre cada archivo en el diccionario.
for nombre_logico, ruta in archivos.items():
    print(f"\n🧾 Analizando: {ruta}")
    # Lee el archivo CSV y obtiene un DataFrame.
    df = leer_csv_con_reemplazo(ruta)
    if df is not None:
        # Analiza el DataFrame para detectar caracteres no válidos.
        caracteres = analizar_caracteres_invalidos(df)
        reportes[nombre_logico] = caracteres
        # Imprime los caracteres sospechosos encontrados.
        print(f"Caracteres sospechosos en {nombre_logico}: {sorted(caracteres)}")
    else:
        # Si hubo un error al leer el archivo, se registra un error en el reporte.
        reportes[nombre_logico] = {"ERROR"}

# ---------- OPCIONAL: GUARDAR REPORTE COMO ARCHIVO ----------

# Guarda el reporte de caracteres sospechosos en un archivo de texto.
with open("docs/reporte_caracteres_sospechosos.txt", "w", encoding="utf-8") as f:
    for nombre_logico, caracteres in reportes.items():
        f.write(f"{nombre_logico}:\n")
        for char in sorted(caracteres):
            f.write(f"  {repr(char)}\n")
        f.write("\n")

print("\n✅ Análisis completo. Verifica 'reporte_caracteres_sospechosos.txt'")
