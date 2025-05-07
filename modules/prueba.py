import pandas as pd
from bokeh.plotting import figure, output_file, save
from bokeh.models import (HoverTool, ColumnDataSource, Span, Label,
                         LabelSet, ColorBar, LinearColorMapper)
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
# 2. Distribución geográfica del apellido Rodríguez
# --------------------------------------

def crear_mapa_distribucion():
    print("\n2. Analizando distribución geográfica del apellido Rodríguez...")
    
    if len(rodriguez_provincias) == 0:
        print("No se encontraron datos provinciales del apellido Rodríguez")
        return "No hay datos suficientes para el análisis de distribución geográfica"
    
    # Agrupar y eliminar duplicados
    provincias_ordenadas = rodriguez_provincias.drop_duplicates(subset='provincia_nombre').sort_values('cantidad', ascending=False)
    
    # Crear una nueva columna de colores alternados
    provincias_ordenadas['color'] = ["#C70039" if i % 2 == 0 else "#1F77B4" for i in range(len(provincias_ordenadas))]
    
    # Crear una nueva columna para la cantidad en miles
    provincias_ordenadas['cantidad_miles'] = provincias_ordenadas['cantidad'] / 1000
    
    source = ColumnDataSource(provincias_ordenadas)
    
    # Crear gráfico de barras con un tamaño mayor
    p = figure(x_range=provincias_ordenadas['provincia_nombre'], 
               width=1200, height=600,  # Aumentar el tamaño del gráfico
               title="Distribución del Apellido Rodríguez por Provincia",
               toolbar_location="right",
               title_location="above")  # Ubicación del título
    
    # Ajustar el tamaño de la fuente del título
    p.title.text_font_size = "20pt"  # Aumentar tamaño del título
    p.title.standoff = 20  # Aumentar padding inferior del título
    p.title.align = "center"  # Centrar el título
    
    # Ajustar títulos de los ejes
    p.xaxis.axis_label = "Provincia"
    p.yaxis.axis_label = "Cantidad de personas (en miles)"  # Modificar título del eje Y
    p.yaxis.axis_label_standoff = 15  # Aumentar padding del título del eje Y
    p.xaxis.axis_label_text_font_size = "16pt"  # Aumentar tamaño del título del eje X
    p.yaxis.axis_label_text_font_size = "16pt"  # Aumentar tamaño del título del eje Y
    
    # Crear barras usando la nueva columna de colores
    p.vbar(x='provincia_nombre', top='cantidad_miles', width=0.8, source=source,
           fill_color='color')  # Referenciar la columna de colores
    
    # Configuración del gráfico
    p.xaxis.major_label_orientation = 3.14/4  # Rotar etiquetas del eje X
    p.yaxis.formatter.use_scientific = False  # Desactivar notación científica
    
    # Eliminar cuadrícula del fondo
    p.grid.grid_line_color = None
    
    # Añadir información interactiva
    hover = HoverTool()
    hover.tooltips = [
        ("Provincia", "@provincia_nombre"),
        ("Cantidad", "@cantidad personas")
    ]
    p.add_tools(hover)
    
    # Guardar y mostrar
    output_file("visualizaciones/rodriguez_distribucion_geografica.html")
    save(p)
    print(f"Gráfico guardado en visualizaciones/rodriguez_distribucion_geografica.html")
    
    # Calcular información adicional
    total_personas = provincias_ordenadas['cantidad'].sum() / 1000  # Total en miles
    max_provincia = provincias_ordenadas.iloc[0]['provincia_nombre']
    max_cantidad = provincias_ordenadas.iloc[0]['cantidad'] / 1000  # Máxima cantidad en miles
    
    return f"En total hay {total_personas} mil personas con el apellido Rodríguez en Argentina. " \
           f"La mayor concentración se encuentra en {max_provincia} con {max_cantidad} mil personas."

print(crear_mapa_distribucion())