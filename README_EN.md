# Data Analysis Project: Database Cleaning and Transformation

This project focuses on cleaning and transforming various databases related to surnames and names, with the objective of optimizing their use for subsequent analysis. The following describes the actions performed on the data, from initial loading to final cleaning.

## Table of Contents
- [1. Introduction](#1-introduction)
- [2. Materials Used](#2-materials-used)
- [3. Data Loading](#3-data-loading)
- [4. Data Inspection](#4-data-inspection)
- [5. Data Cleaning](#5-data-cleaning)
- [6. Data Transformation](#6-data-transformation)
- [7. Conclusions](#7-conclusions)
- [8. Links](#8-links)

## 1. Introduction
The objective of this project is to prepare datasets for deeper analysis, ensuring that the data is consistent, clean, and ready for use. We worked with CSV files containing information about surnames and names, which presented suspicious characters and encoding errors.

## 2. Materials Used

### `data_cleaning` Folder

1. **Reemplazo_caracteres.py**
   - Contains functions to clean and correct characters in CSV file texts. Uses a replacement dictionary that maps erroneous characters to their correct equivalents.

2. **AnalisisContexto.py**
   - Handles analyzing the contexts in which suspicious characters appear in the data. Includes functions to read CSV files, extract contexts, and generate reports about found characters.

3. **DataCleaning.py**
   - Contains functions to detect invalid characters in CSV file texts. Performs initial analysis to identify data quality issues.

### `docs` Folder

1. **historico-nombres_clean.csv** (221MB)
   - Clean version of the original dataset `historico-nombres.csv`, contains information about historical names, corrected of suspicious characters.

2. **apellidos_mas_frecuentes_provincia_clean.csv** 
   - Contains the most frequent surnames by province, in its clean version.

3. **apellidos_mas_frecuentes_pais_clean.csv** (397B, 22 lines)
   - Presents the most common surnames at national level, also in its clean version.

4. **apellidos_cantidad_personas_provincia_clean.csv** (8.3MB)
   - Data about the number of people with specific surnames in each province, in its clean version.

5. **reporte_caracteres_sospechosos.txt** (1.3KB, 153 lines)
   - Documents suspicious characters found in analyzed files.

6. **reporte_contextos.txt** (8.3KB, 530 lines)
   - Contains examples of contexts in which suspicious characters appear.

7. **historico-nombres.csv** (211MB)
   - Original file containing historical names data, before being cleaned.

8. **apellidos_cantidad_personas_provincia.csv** (9.5MB)
   - Original file containing information about the number of people with surnames in each province.

9. **apellidos_mas_frecuentes_provincia.csv** (17KB, 482 lines)
   - Original file presenting the most frequent surnames by province, before cleaning.

10. **apellidos_mas_frecuentes_pais.csv** (443B, 22 lines)
    - Original file showing the most common surnames at national level, with encoding issues.

## 3. Data Loading
Data was loaded from CSV files using the `pandas` library. A `leer_csv_con_reemplazo` function was implemented that allows handling encoding errors when reading files.

```python
def leer_csv_con_reemplazo(path):
    try:
        with open(path, encoding='utf-8', errors='replace') as f:
            contenido = f.read()
        return pd.read_csv(StringIO(contenido))
    except Exception as e:
        print(f"Error reading {path}: {e}")
        return None
```

## 4. Data Inspection
Once data was loaded, an initial inspection was performed to identify suspicious characters that could affect the analysis. The `analizar_caracteres_invalidos` function was used, which traverses each object-type column and detects non-ASCII characters.

```python
def analizar_caracteres_invalidos(df):
    caracteres_sospechosos = set()
    for columna in df.select_dtypes(include='object').columns:
        for valor in df[columna].dropna():
            caracteres_sospechosos.update(detectar_caracteres_invalidos(valor))
    return caracteres_sospechosos
```

## 5. Data Cleaning
Data cleaning was carried out through the `limpiar_archivo` function, which applies a replacement dictionary to correct erroneous characters in texts. This process includes normalizing column names and creating clean CSV files.

```python
def limpiar_archivo(nombre_logico, ruta_archivo, encoding='utf-8'):
    # Data loading and cleaning
    ...
    df.to_csv(output_name, index=False)
```

## 6. Data Transformation
After cleaning, reports were generated that document suspicious characters found in each file. This was accomplished through the `recolectar_contextos` function, which extracts context examples for each suspicious character.

```python
def recolectar_contextos(df, caracteres_sospechosos, max_ejemplos=3):
    contextos = defaultdict(lambda: defaultdict(set))
    ...
    return contextos
```

## 7. Conclusions
The data cleaning and transformation process is crucial for ensuring the quality of subsequent analyses. This project demonstrates skills in data manipulation, quality issue identification, and implementation of effective solutions.

## 8. Links
- [Leer esto en Español](README.md)