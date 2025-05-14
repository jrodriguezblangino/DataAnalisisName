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
# 4. Análisis específico de Córdoba
# --------------------------------------

# --------------------------------------
# 6. Evolución histórica del nombre Joaquín
# --------------------------------------

def analizar_evolucion_historica():
    print("\n6. Analizando evolución histórica del nombre Joaquín...")
    
    if len(joaquin_historico) == 0:
        print("No se encontraron datos históricos del nombre Joaquín")
        return "No hay datos suficientes para el análisis de evolución histórica"
    
    # Agrupar por año y sumar
    joaquin_por_anio = joaquin_historico.groupby('anio')['cantidad'].sum().reset_index()
    
        # Crear gráfico interactivo con Bokeh
    source = ColumnDataSource(joaquin_por_anio)
    
    p = figure(width=1080, height=600, 
              title="Evolución Histórica del Nombre Joaquín",
              title_location="above",
              x_axis_label="Año", y_axis_label="Cantidad de Nacimientos",
              toolbar_location="right")
    
    # Ajustar el tamaño de la fuente del título
    p.title.text_font_size = "18pt"  # Tamaño del título
    p.title.standoff = 20  # Espaciado inferior del título
    p.title.align = "center"  # Centrar el título


    #Ajustar el tamaño y el estilo del eje Y

    p.yaxis.axis_label_text_font_size = "14pt"
    p.yaxis.axis_label_text_font_style = "bold"
    p.yaxis.axis_label_standoff = 15
   
   

    # Línea de tendencia
    line = p.line('anio', 'cantidad', source=source, line_width=2, 
                 line_color='#1F77B4', legend_label="Joaquín")
    
    # Añadir marcadores
    circles = p.circle('anio', 'cantidad', source=source, size=8, 
                      color='#1F77B4', fill_alpha=0.4)
    
    # Agregar información interactiva
    hover = HoverTool(renderers=[circles], tooltips=[
        ("Año", "@anio"),
        ("Nacimientos", "@cantidad")
    ])
    p.add_tools(hover)
    
    # Configuración
    p.legend.location = "top_left"
    p.legend.click_policy = "hide"
    
    # Guardar y mostrar
    output_file("visualizaciones/joaquin_evolucion_historica.html")
    save(p)
    print(f"Gráfico guardado en visualizaciones/joaquin_evolucion_historica.html")
    
    # Calcular algunos insights
    anio_min = joaquin_por_anio['anio'].min()
    anio_max = joaquin_por_anio['anio'].max()
    cantidad_min = joaquin_por_anio['cantidad'].min()
    cantidad_max = joaquin_por_anio['cantidad'].max()

analizar_evolucion_historica()
