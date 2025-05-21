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

# Variable global para almacenar la estimación
estimacion_joaquin_rodriguez = 0

def estimar_unicidad_combinacion():
    global estimacion_joaquin_rodriguez  # Hacer que la variable sea global
    print("\n10. Estimando unicidad de la combinación Joaquín Rodríguez...")
    
    if len(rodriguez_pais) == 0 or len(joaquin_historico) == 0:
        print("No hay datos suficientes para estimar la unicidad de la combinación")
        return "No hay datos suficientes para estimar la unicidad de la combinación"
    
    # Obtener porcentaje del apellido Rodríguez
    porcentaje_rodriguez = rodriguez_pais['porcentaje_de_poblacion_portadora'].values[0] / 100
    
    # Estimar la frecuencia del nombre Joaquín
    ultimo_periodo = joaquin_historico.loc[joaquin_historico['anio'].idxmax()]
    anio_reciente = ultimo_periodo['anio']
    
    # Obtener todos los nombres del mismo periodo para calcular proporción
    if 'anio' in historico_nombres.columns:
        nombres_mismo_periodo = historico_nombres[historico_nombres['anio'] == anio_reciente]
        total_nacimientos_periodo = nombres_mismo_periodo['cantidad'].sum()
        nacimientos_joaquin_periodo = joaquin_historico[joaquin_historico['anio'] == anio_reciente]['cantidad'].sum()
        
        if total_nacimientos_periodo > 0:
            porcentaje_joaquin = nacimientos_joaquin_periodo / total_nacimientos_periodo
        else:
            porcentaje_joaquin = 0  # Asegurarse de que no sea cero
    else:
        porcentaje_joaquin = 0  # Asegurarse de que no sea cero
    
    # Estimar población total de Argentina (aproximadamente 45 millones)
    poblacion_argentina = 45000000
    
    # Calcular estimación de personas con el apellido Rodríguez
    personas_rodriguez = poblacion_argentina * porcentaje_rodriguez
    
    # Calcular estimación de personas llamadas Joaquín Rodríguez
    estimacion_joaquin_rodriguez = personas_rodriguez * porcentaje_joaquin
    
    # Crear visualización
    labels = ['Apellido Rodríguez', 'Nombre Joaquín', 'Joaquín Rodríguez']
    valores = [personas_rodriguez, poblacion_argentina * porcentaje_joaquin, estimacion_joaquin_rodriguez]
    
    # Verificar valores
    print(f"Valores para el gráfico: {valores}")
    
    # Asegurarse de que todos los valores sean mayores que cero
    if any(v <= 0 for v in valores):
        print("Error: Uno o más valores son cero o negativos. Ajustando a 1 para la visualización.")
        valores = [max(v, 1) for v in valores]  # Ajustar a 1 para evitar problemas con la escala logarítmica
    
    # Crear colores para las barras
    colores = ["#1F77B4", "#C70039", "#2CA02C"]
    
    source = ColumnDataSource(data=dict(labels=labels, valores=valores, colores=colores))
    
    p = figure(x_range=labels, width=1080, height=600,
               title="Estimación de Personas con el Nombre y Apellido",
               toolbar_location="right")  # Cambiar a escala lineal
    
    p.vbar(x='labels', top='valores', width=0.4, source=source,
           color='colores')  # Usar la columna de colores
    
    p.y_range.start = 1  # Comenzar desde 1 en escala lineal
    p.xgrid.grid_line_color = None
    p.yaxis.axis_label = "Estimación de Personas"
    p.xaxis.major_label_orientation = 3.14/4

    # Ajustar el tamaño de la fuente del título
    p.title.text_font_size = "18pt"  # Tamaño del título
    p.title.standoff = 20  # Espaciado inferior del título
    p.title.align = "center"  # Centrar el título

    # Ajustar el tamaño y el estilo del eje Y
    p.yaxis.axis_label_text_font_size = "14pt"
    p.yaxis.axis_label_text_font_style = "bold"
    p.yaxis.axis_label_standoff = 15

    # Ajustar el tamaño y el estilo del eje x
    p.xaxis.axis_label_text_font_size = "15pt"
    p.xaxis.axis_label_text_font_style = "bold"
    p.xaxis.axis_label_standoff = 15

    # Eliminar la cuadrícula
    p.xgrid.visible = False  
    p.ygrid.visible = False 
    
    # Formatear el eje Y para evitar notación científica
    p.yaxis.formatter = NumeralTickFormatter(format="0,0")  # Formato sin notación científica
    
    # Información interactiva
    hover = HoverTool()
    hover.tooltips = [
        ("Categoría", "@labels"),
        ("Estimación", "@valores{0,0}")
    ]
    p.add_tools(hover)
    
    # Guardar y mostrar
    output_file("visualizaciones/joaquin_unicidad_combinacion.html")
    save(p)
    print(f"Gráfico guardado en visualizaciones/joaquin_unicidad_combinacion.html")
    
    # Retornar un resumen de la estimación
    return f"Se estima que hay aproximadamente {estimacion_joaquin_rodriguez:.0f} personas llamadas Joaquín Rodríguez en Argentina."


estimar_unicidad_combinacion()