import pandas as pd
import re
from io import StringIO
from collections import defaultdict

# ---------- UTILIDADES ----------

def leer_csv_con_reemplazo(path):
    try:
        with open(path, encoding='utf-8', errors='replace') as f:
            contenido = f.read()
        return pd.read_csv(StringIO(contenido))
    except Exception as e:
        print(f"Error leyendo {path}: {e}")
        return None

def extraer_contexto(texto, char, ventana=10):
    posiciones = [m.start() for m in re.finditer(re.escape(char), texto)]
    contextos = []
    for pos in posiciones:
        inicio = max(pos - ventana, 0)
        fin = min(pos + ventana + 1, len(texto))
        contexto = texto[inicio:fin].replace('\n', ' ').strip()
        contextos.append(contexto)
    return contextos

def recolectar_contextos(df, caracteres_sospechosos, max_ejemplos=3):
    contextos = defaultdict(lambda: defaultdict(set))
    for col in df.select_dtypes(include='object').columns:
        for valor in df[col].dropna():
            if not isinstance(valor, str):
                continue
            for char in caracteres_sospechosos:
                if char in valor and len(contextos[col][char]) < max_ejemplos:
                    ejemplos = extraer_contexto(valor, char)
                    for ej in ejemplos:
                        if len(contextos[col][char]) < max_ejemplos:
                            contextos[col][char].add(ej)
    return contextos

# ---------- ARCHIVOS A ANALIZAR ----------

archivos = {
    "apellidos_provincia": "docs/apellidos_cantidad_personas_provincia.csv",
    "apellidos_pais": "docs/apellidos_mas_frecuentes_pais.csv",
    "apellidos_provincia_ranking": "docs/apellidos_mas_frecuentes_provincia.csv",
    "historico-nombres": "docs/historico-nombres.csv"
}

# ---------- PROCESAMIENTO CON CONTEXTO ----------

reporte_completo = {}

for nombre_logico, ruta in archivos.items():
    print(f"\n📄 Procesando {ruta}...")
    df = leer_csv_con_reemplazo(ruta)
    if df is not None:
        caracteres = set()
        for col in df.select_dtypes(include='object').columns:
            for val in df[col].dropna():
                if isinstance(val, str):
                    encontrados = re.findall(r'[^\x00-\x7F]', val)
                    caracteres.update(encontrados)
        contextos = recolectar_contextos(df, caracteres)
        reporte_completo[nombre_logico] = contextos
    else:
        print(f"⚠️ No se pudo procesar {ruta}.")

# ---------- GUARDAR REPORTE DE CONTEXTOS ----------

with open("docs/reporte_contextos.txt", "w", encoding="utf-8") as f:
    for archivo, columnas in reporte_completo.items():
        f.write(f"\n=== Archivo: {archivo} ===\n")
        for columna, chars in columnas.items():
            f.write(f"\nColumna: {columna}\n")
            for char, ejemplos in chars.items():
                f.write(f"\n  Carácter: {repr(char)}\n")
                for ej in ejemplos:
                    f.write(f"    -> {ej}\n")

print("\n✅ Contextos guardados en 'reporte_contextos.txt'. Revisá los ejemplos para decidir qué reemplazar.")
