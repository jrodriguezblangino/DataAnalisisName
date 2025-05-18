import pandas as pd
from bokeh.plotting import figure, output_file, save
from bokeh.models import (HoverTool, ColumnDataSource, Span, Label,
                         LabelSet, ColorBar, LinearColorMapper,NumeralTickFormatter)
from bokeh.layouts import column, row, gridplot
from bokeh.transform import factor_cmap, transform, linear_cmap
from bokeh.palettes import Viridis256
from bokeh.models import GeoJSONDataSource
import warnings
import os
import geopandas as gpd
from bokeh.io import export_png
warnings.filterwarnings('ignore')

# Verificar y crear el directorio
if not os.path.exists("visualizaciones"):
    os.makedirs("visualizaciones")
    print("Directorio 'visualizaciones' creado.")

# Cargar datos limpios
print("Cargando datos limpios...")
apellidos_provincia = pd.read_csv('docs/apellidos_cantidad_personas_provincia_clean.csv')
apellidos_pais = pd.read_csv('docs/apellidos_mas_frecuentes_pais_clean.csv')
apellidos_provincia_ranking = pd.read_csv('docs/apellidos_mas_frecuentes_provincia_clean.csv')
historico_nombres = pd.read_csv('docs/historico-nombres_clean.csv')

# Preparar datos relevantes para el análisis
print("Preparando datasets específicos para el análisis...")

# Buscar el apellido Rodríguez (probar con y sin tilde)
rodriguez_pais = apellidos_pais[apellidos_pais['apellido'].str.lower() == 'rodriguez']
if len(rodriguez_pais) == 0:
    rodriguez_pais = apellidos_pais[apellidos_pais['apellido'].str.lower() == 'rodríguez']

rodriguez_provincias = apellidos_provincia[apellidos_provincia['apellido'].str.lower() == 'rodriguez']
if len(rodriguez_provincias) == 0:
    rodriguez_provincias = apellidos_provincia[apellidos_provincia['apellido'].str.lower() == 'rodríguez']

rodriguez_provincias = rodriguez_provincias.groupby('provincia_nombre').agg({'cantidad': 'sum'}).reset_index()

rodriguez_ranking_provincias = apellidos_provincia_ranking[apellidos_provincia_ranking['apellido'].str.lower() == 'rodriguez']
if len(rodriguez_ranking_provincias) == 0:
    rodriguez_ranking_provincias = apellidos_provincia_ranking[apellidos_provincia_ranking['apellido'].str.lower() == 'rodríguez']

# Buscar el nombre Joaquín (probar con y sin tilde)
joaquin_historico = historico_nombres[historico_nombres['nombre'].str.lower() == 'joaquin']
if len(joaquin_historico) == 0:
    joaquin_historico = historico_nombres[historico_nombres['nombre'].str.lower() == 'joaquín']

# Imprimir las columnas de joaquin_historico para verificar
print("Columnas de joaquin_historico:", joaquin_historico.columns)

# Asegúrate de que la columna 'provincia_nombre' existe
if 'provincia_nombre' in joaquin_historico.columns:
    # Crear un DataFrame que contenga la cantidad de Joaquín por provincia
    joaquin_por_provincia = joaquin_historico.groupby('provincia_nombre')['cantidad'].sum().reset_index()
    joaquin_por_provincia.rename(columns={'cantidad': 'cantidad_joaquin'}, inplace=True)
else:
    print("Error: 'provincia_nombre' no se encuentra en joaquin_historico.")
    # Aquí puedes manejar el error como desees, por ejemplo, asignar un DataFrame vacío o lanzar una excepción.
    joaquin_por_provincia = pd.DataFrame(columns=['provincia_nombre', 'cantidad_joaquin'])

# Ahora, combinamos este DataFrame con rodriguez_provincias
rodriguez_provincias = rodriguez_provincias.merge(joaquin_por_provincia, on='provincia_nombre', how='left')

# Ordenar datos históricos por año
if 'anio' in joaquin_historico.columns:
    joaquin_historico = joaquin_historico.sort_values('anio')
    
# Imprimir información básica para verificar
print(f"\nDatos de apellido Rodríguez a nivel país: {len(rodriguez_pais)} registros")
print(f"Datos de apellido Rodríguez por provincia: {len(rodriguez_provincias)} registros")
print(f"Datos de ranking de Rodríguez por provincia: {len(rodriguez_ranking_provincias)} registros")
print(f"Datos históricos del nombre Joaquín: {len(joaquin_historico)} registros")

# --------------------------------------
# 9. Comparativa generacional del nombre Joaquín
# --------------------------------------

def analizar_generaciones():
    print("\n9. Analizando popularidad del nombre Joaquín por generaciones...")
    
    if len(joaquin_historico) == 0:
        print("No se encontraron datos históricos del nombre Joaquín")
        return "No hay datos suficientes para el análisis generacional"
    
    # Definir rangos generacionales (aproximados)
    generaciones = {
        '1928-1945': (1928, 1945),
        '1946-1964': (1946, 1964),
        '1965-1980': (1965, 1980),
        '1981-1996': (1981, 1996),
        '1997-2012': (1997, 2012),
        '2013- Actualidad': (2013, 2030)
    }
    
    # Preparar datos para el análisis generacional
    datos_generacionales = []
    
    for gen_nombre, (inicio, fin) in generaciones.items():
        # Filtrar datos para esta generación
        gen_data = joaquin_historico[
            (joaquin_historico['anio'] >= inicio) & 
            (joaquin_historico['anio'] <= fin)
        ]
        
        if len(gen_data) > 0:
            total = gen_data['cantidad'].sum()
            promedio_anual = total / (fin - inicio + 1)
            datos_generacionales.append({
                'generacion': gen_nombre,
                'total': total,
                'promedio_anual': promedio_anual,
                'periodo': f"{inicio}-{fin}"
            })
    
    # Convertir a DataFrame
    df_generaciones = pd.DataFrame(datos_generacionales)
    
    # Agregar una columna de colores
    df_generaciones['color'] = ["#1F77B4" if i % 2 == 0 else "#C70039" for i in range(len(df_generaciones))]
    
    if len(df_generaciones) == 0:
        return "No hay datos suficientes para realizar el análisis generacional"
    
    # Crear visualización
    source = ColumnDataSource(df_generaciones)
    
    p = figure(x_range=df_generaciones['generacion'], width=1080, height=600,
               title="Popularidad del Nombre Joaquín por Generación",
               toolbar_location="right")
    
    # Ajustar el tamaño de la fuente del título
    p.title.text_font_size = "18pt"  # Tamaño del título
    p.title.standoff = 20  # Espaciado inferior del título
    p.title.align = "center"  # Centrar el título

    # Ajustar el tamaño y el estilo del eje Y
    p.yaxis.axis_label_text_font_size = "14pt"
    p.yaxis.axis_label_text_font_style = "bold"
    p.yaxis.axis_label_standoff = 15

    # Ajustar el tamaño y el estilo del eje x
    p.xaxis.axis_label_text_font_size = "12pt"
    p.xaxis.axis_label_text_font_style = "bold"
    p.xaxis.axis_label_standoff = 15

    # Eliminar la cuadrícula
    p.xgrid.visible = False  # Desactivar cuadrícula del eje x
    p.ygrid.visible = False  # Desactivar cuadrícula del eje y

    # Barras para total con intercalación de colores
    p.vbar(x='generacion', top='total', width=0.6, source=source,
           color='color', legend_label="Total Nacimientos")
    
    # Configuración
    p.xaxis.major_label_orientation = 3.14/4
    p.yaxis.axis_label = "Total de Nacimientos"
    p.legend.location = "top_left"
    
    # Información interactiva
    hover = HoverTool()
    hover.tooltips = [
        ("Generación", "@generacion"),
        ("Periodo", "@periodo"),
        ("Total Nacimientos", "@total"),
        ("Promedio Anual", "@promedio_anual{0.0}")
    ]
    p.add_tools(hover)
    
    # Guardar y mostrar
    output_file("visualizaciones/joaquin_analisis_generacional.html")
    save(p)
    print(f"Gráfico guardado en visualizaciones/joaquin_analisis_generacional.html")
    
    # Generar insights
    gen_popular = df_generaciones.loc[df_generaciones['promedio_anual'].idxmax(), 'generacion']
    prom_max = df_generaciones['promedio_anual'].max()
    
    return f"El nombre Joaquín ha sido más popular durante la {gen_popular}, "\
           f"con un promedio de {prom_max:.0f} nacimientos por año."

analizar_generaciones()