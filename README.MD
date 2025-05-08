# Proyecto de Análisis de Datos: Limpieza y Transformación de Bases de Datos

Este proyecto se centra en la limpieza y transformación de diversas bases de datos relacionadas con apellidos y nombres, con el objetivo de optimizar su uso para análisis posteriores. A continuación, se describen las acciones realizadas sobre los datos, desde la carga inicial hasta la limpieza final.

## Tabla de Contenidos
- [1. Introducción](#1-introducción)
- [2. Materiales Utilizados](#2-materiales-utilizados)
- [3. Carga de Datos](#3-carga-de-datos)
- [4. Inspección de Datos](#4-inspección-de-datos)
- [5. Limpieza de Datos](#5-limpieza-de-datos)
- [6. Transformación de Datos](#6-transformación-de-datos)
- [7. Conclusiones](#7-conclusiones)
- [8. Enlaces](#8-enlaces)

## 1. Introducción
El objetivo de este proyecto es preparar conjuntos de datos para un análisis más profundo, asegurando que los datos sean consistentes, limpios y listos para su uso. Se trabajó con archivos CSV que contenían información sobre apellidos y nombres, los cuales presentaban caracteres sospechosos y errores de codificación.

## 2. Materiales Utilizados

### Carpeta `data_cleaning`

1. **Reemplazo_caracteres.py**
   - Contiene funciones para limpiar y corregir caracteres en los textos de los archivos CSV. Utiliza un diccionario de reemplazos que mapea caracteres erróneos a sus equivalentes correctos.

2. **AnalisisContexto.py**
   - Se encarga de analizar los contextos en los que aparecen caracteres sospechosos en los datos. Incluye funciones para leer archivos CSV, extraer contextos y generar reportes sobre los caracteres encontrados.

3. **DataCleaning.py**
   - Contiene funciones para detectar caracteres inválidos en los textos de los archivos CSV. Realiza un análisis inicial para identificar problemas de calidad en los datos.

### Carpeta `docs`

1. **historico-nombres_clean.csv** (221MB)
   - Versión limpia del conjunto de datos original `historico-nombres.csv`, contiene información sobre nombres históricos, corregidos de caracteres sospechosos.

2. **apellidos_mas_frecuentes_provincia_clean.csv** 
   - Contiene los apellidos más frecuentes por provincia, en su versión limpia.

3. **apellidos_mas_frecuentes_pais_clean.csv** (397B, 22 líneas)
   - Presenta los apellidos más comunes a nivel nacional, también en su versión limpia.

4. **apellidos_cantidad_personas_provincia_clean.csv** (8.3MB)
   - Datos sobre la cantidad de personas con apellidos específicos en cada provincia, en su versión limpia.

5. **reporte_caracteres_sospechosos.txt** (1.3KB, 153 líneas)
   - Documenta los caracteres sospechosos encontrados en los archivos analizados.

6. **reporte_contextos.txt** (8.3KB, 530 líneas)
   - Contiene ejemplos de contextos en los que aparecen caracteres sospechosos.

7. **historico-nombres.csv** (211MB)
   - Archivo original que contiene datos sobre nombres históricos, antes de ser limpiado.

8. **apellidos_cantidad_personas_provincia.csv** (9.5MB)
   - Archivo original que contiene información sobre la cantidad de personas con apellidos en cada provincia.

9. **apellidos_mas_frecuentes_provincia.csv** (17KB, 482 líneas)
   - Archivo original que presenta los apellidos más frecuentes por provincia, antes de la limpieza.

10. **apellidos_mas_frecuentes_pais.csv** (443B, 22 líneas)
    - Archivo original que muestra los apellidos más comunes a nivel nacional, con problemas de codificación.

## 3. Carga de Datos
Los datos se cargaron desde archivos CSV utilizando la biblioteca `pandas`. Se implementó una función `leer_csv_con_reemplazo` que permite manejar errores de codificación al leer los archivos.

```python
def leer_csv_con_reemplazo(path):
    try:
        with open(path, encoding='utf-8', errors='replace') as f:
            contenido = f.read()
        return pd.read_csv(StringIO(contenido))
    except Exception as e:
        print(f"Error leyendo {path}: {e}")
        return None
```

## 4. Inspección de Datos
Una vez cargados los datos, se realizó una inspección inicial para identificar caracteres sospechosos que podrían afectar el análisis. Se utilizó la función `analizar_caracteres_invalidos`, que recorre cada columna de tipo objeto y detecta caracteres no ASCII.

```python
def analizar_caracteres_invalidos(df):
    caracteres_sospechosos = set()
    for columna in df.select_dtypes(include='object').columns:
        for valor in df[columna].dropna():
            caracteres_sospechosos.update(detectar_caracteres_invalidos(valor))
    return caracteres_sospechosos
```

## 5. Limpieza de Datos
La limpieza de datos se llevó a cabo mediante la función `limpiar_archivo`, que aplica un diccionario de reemplazos para corregir caracteres erróneos en los textos. Este proceso incluye la normalización de nombres de columnas y la creación de archivos CSV limpios.

```python
def limpiar_archivo(nombre_logico, ruta_archivo, encoding='utf-8'):
    # Carga y limpieza de datos
    ...
    df.to_csv(output_name, index=False)
```

## 6. Transformación de Datos
Después de la limpieza, se generaron reportes que documentan los caracteres sospechosos encontrados en cada archivo. Esto se realizó mediante la función `recolectar_contextos`, que extrae ejemplos de contexto para cada carácter sospechoso.

```python
def recolectar_contextos(df, caracteres_sospechosos, max_ejemplos=3):
    contextos = defaultdict(lambda: defaultdict(set))
    ...
    return contextos
```

## 7. Conclusiones
El proceso de limpieza y transformación de datos es crucial para garantizar la calidad de los análisis posteriores. Este proyecto demuestra habilidades en la manipulación de datos, la identificación de problemas de calidad y la implementación de soluciones efectivas.

## 8. Enlaces
- [Read this in English](README_EN.md)
