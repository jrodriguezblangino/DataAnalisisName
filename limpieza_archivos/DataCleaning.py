import pandas as pd
import re
from io import StringIO

# ---------- FUNCIONES BASE ----------

def leer_csv_con_reemplazo(path):
    try:
        with open(path, encoding='utf-8', errors='replace') as f:
            contenido = f.read()
        return pd.read_csv(StringIO(contenido))
    except Exception as e:
        print(f"Error leyendo {path}: {e}")
        return None

def detectar_caracteres_invalidos(texto):
    if not isinstance(texto, str):
        return set()
    patron = re.compile(r'[^\x00-\x7F]+')
    return set(patron.findall(texto))

def analizar_caracteres_invalidos(df):
    caracteres_sospechosos = set()
    for columna in df.select_dtypes(include='object').columns:
        for valor in df[columna].dropna():
            caracteres_sospechosos.update(detectar_caracteres_invalidos(valor))
    return caracteres_sospechosos

# ---------- PROCESO PARA TODOS LOS ARCHIVOS ----------

archivos = {
    "apellidos_provincia": "docs/apellidos_cantidad_personas_provincia.csv",
    "apellidos_pais": "docs/apellidos_mas_frecuentes_pais.csv",
    "apellidos_provincia_ranking": "docs/apellidos_mas_frecuentes_provincia.csv",
    "historico-nombres": "docs/historico-nombres.csv"
}

reportes = {}

for nombre_logico, ruta in archivos.items():
    print(f"\n🧾 Analizando: {ruta}")
    df = leer_csv_con_reemplazo(ruta)
    if df is not None:
        caracteres = analizar_caracteres_invalidos(df)
        reportes[nombre_logico] = caracteres
        print(f"Caracteres sospechosos en {nombre_logico}: {sorted(caracteres)}")
    else:
        reportes[nombre_logico] = {"ERROR"}

# ---------- OPCIONAL: GUARDAR REPORTE COMO ARCHIVO ----------

with open("docs/reporte_caracteres_sospechosos.txt", "w", encoding="utf-8") as f:
    for nombre_logico, caracteres in reportes.items():
        f.write(f"{nombre_logico}:\n")
        for char in sorted(caracteres):
            f.write(f"  {repr(char)}\n")
        f.write("\n")

print("\n✅ Análisis completo. Verifica 'reporte_caracteres_sospechosos.txt'")
