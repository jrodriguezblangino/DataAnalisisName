import pandas as pd
from bokeh.plotting import figure, output_file, save
from bokeh.models import (HoverTool, ColumnDataSource, Span, Label,
                         LabelSet, ColorBar, LinearColorMapper, NumeralTickFormatter)
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



# 3. Comparativa entre provincias
# --------------------------------------

def comparar_provincias():
    print("\nComparando presencia del apellido Rodríguez entre provincias...")
    
    if len(rodriguez_provincias) == 0:
        print("No se encontraron datos provinciales del apellido Rodríguez")
        return "No hay datos suficientes para la comparativa entre provincias"
    
    # Ordenar provincias por cantidad
    top_provincias = rodriguez_provincias.sort_values('cantidad', ascending=False)
    
    # Seleccionar top 5 y bottom 5
    top5 = top_provincias.head(5)
    bottom5 = top_provincias.tail(5)
    
    # Combinar para visualización
    combined = pd.concat([top5, bottom5])
    combined = combined.sort_values('cantidad', ascending=True)
    
    # Crear colores para las barras
    colores = ['#C70039'] * 5 + ['#1F77B4'] * 5
    combined['color'] = colores  # Agregar la columna de colores
    
    # Crear gráfico
    source = ColumnDataSource(combined)
    
    p = figure(y_range=combined['provincia_nombre'], width=800, height=400,
              title="Provincias con Mayor y Menor Presencia del Apellido Rodríguez",
              toolbar_location="right")
    
    # Ajustar el tamaño de la fuente del título
    p.title.text_font_size = "12pt"  # Aumentar tamaño del título
    p.title.standoff = 20  # Aumentar padding inferior del título
    p.title.align = "center"  # Centrar el título
    
    # Crear barras
    bars = p.hbar(y='provincia_nombre', right='cantidad', height=0.8, 
                  source=source, color='color')  # Usar la columna 'color'
    
    # Configuración del eje X
    p.xaxis.axis_label = "Cantidad de personas"
    p.xaxis.axis_label_text_font_size = "12pt"
    p.xaxis.axis_label_text_font_style = "bold"
    p.xaxis.axis_label_standoff = 15
    p.xgrid.grid_line_color = None
    
    # Formatear los números del eje X
    p.xaxis.formatter = NumeralTickFormatter(format="0,0")

    # Añadir etiquetas
    labels = LabelSet(x='cantidad', y='provincia_nombre', text='cantidad', 
                     source=source, x_offset=5, text_font_size='8pt')
    p.add_layout(labels)
    
    # Información interactiva
    hover = HoverTool()
    hover.tooltips = [
        ("Provincia", "@provincia_nombre"),
        ("Cantidad", "@cantidad personas")
    ]
    p.add_tools(hover)
    
    # Guardar y mostrar
    output_file("visualizaciones/rodriguez_comparativa_provincias_prueba.html")
    save(p)
    print(f"Gráfico guardado en visualizaciones/rodriguez_comparativa_provincias_prueba.html")
    
    # Calcular algunos datos interesantes
    provincia_max = top5.iloc[0]['provincia_nombre']
    cantidad_max = top5.iloc[0]['cantidad']
    provincia_min = bottom5.iloc[0]['provincia_nombre']
    cantidad_min = bottom5.iloc[0]['cantidad']
    
    return f"La provincia con mayor presencia del apellido Rodríguez es {provincia_max} "\
           f"con {cantidad_max} personas, mientras que la provincia con menor presencia "\
           f"es {provincia_min} con {cantidad_min} personas."

# Llama a la función para probar
comparar_provincias()
