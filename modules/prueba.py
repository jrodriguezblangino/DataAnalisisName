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

def generar_mapa_distribucion_argentina():
    """
    Genera un mapa de calor de Argentina con la distribución de Rodríguez, Joaquín y la combinación.
    
    Utiliza los datos reales de rodriguez_provincias y joaquin_historico para crear
    visualizaciones geográficas de la distribución.
    
    Retorna:
    --------
    str
        Mensaje con la ruta de los archivos guardados
    """
    print("\nGenerando mapa de calor de distribución en Argentina...")
    
    # Usar los datasets globales ya cargados
    global rodriguez_provincias, joaquin_historico, estimacion_joaquin_rodriguez
    
    # Verificar si tenemos los datos necesarios
    if len(rodriguez_provincias) == 0:
        return "No hay datos suficientes sobre el apellido Rodríguez por provincia."
    
    # Preparar datos de Joaquín por provincia
    if 'provincia_nombre' in joaquin_historico.columns:
        # Si ya tenemos los datos por provincia, los agrupamos
        joaquin_por_provincia = joaquin_historico.groupby('provincia_nombre')['cantidad'].sum().reset_index()
        joaquin_por_provincia.rename(columns={'cantidad': 'cantidad_joaquin'}, inplace=True)
    else:
        # Si no tenemos datos por provincia, creamos un DataFrame vacío con la estructura correcta
        print("No se encontraron datos del nombre Joaquín por provincia.")
        joaquin_por_provincia = pd.DataFrame(columns=['provincia_nombre', 'cantidad_joaquin'])
    
    try:
        # Cargar el archivo de shapefile de Argentina
        argentina_map = gpd.read_file("shapefiles/gadm41_ARG_1.shp")
        print(f"Shapefile cargado correctamente con {len(argentina_map)} provincias.")
    except Exception as e:
        print(f"Error al cargar el shapefile: {e}")
        return "Error al cargar el shapefile de Argentina."
    
    # Renombrar columnas para facilitar la unión
    if 'NAME_1' in argentina_map.columns:
        argentina_map = argentina_map.rename(columns={'NAME_1': 'provincia_nombre'})
    
    # Normalizar nombres de provincias para unir correctamente los DataFrames
    def normalizar_nombre(nombre):
        if not isinstance(nombre, str):
            return ""
        
        # Mapeo de nombres que podrían variar
        mapeo = {
            'Ciudad Autónoma de Buenos Aires': 'Ciudad de Buenos Aires',
            'CABA': 'Ciudad de Buenos Aires',
            'Tierra del Fuego': 'Tierra del Fuego, Antártida e Islas del Atlántico Sur',
            'Santiago Del Estero': 'Santiago del Estero'
        }
        
        if nombre in mapeo:
            return mapeo[nombre]
            
        # Normalización general
        return nombre.lower().strip().replace(' ', '_')
    
    # Aplicar normalización a todos los datasets
    argentina_map['provincia_norm'] = argentina_map['provincia_nombre'].apply(normalizar_nombre)
    rodriguez_provincias['provincia_norm'] = rodriguez_provincias['provincia_nombre'].apply(normalizar_nombre)
    
    if len(joaquin_por_provincia) > 0 and 'provincia_nombre' in joaquin_por_provincia.columns:
        joaquin_por_provincia['provincia_norm'] = joaquin_por_provincia['provincia_nombre'].apply(normalizar_nombre)
    
    # Unir datos de Rodríguez con el mapa
    merged_rodriguez = argentina_map.merge(rodriguez_provincias, on='provincia_norm', how='left')
    merged_rodriguez['cantidad'] = merged_rodriguez['cantidad'].fillna(0)
    
    # Unir datos de Joaquín con el mapa
    if len(joaquin_por_provincia) > 0 and 'provincia_norm' in joaquin_por_provincia.columns:
        merged_joaquin = argentina_map.merge(joaquin_por_provincia, on='provincia_norm', how='left')
        merged_joaquin['cantidad_joaquin'] = merged_joaquin['cantidad_joaquin'].fillna(0)
    else:
        # Si no hay datos de Joaquín por provincia, usar el mismo DataFrame de base
        merged_joaquin = merged_rodriguez.copy()
        merged_joaquin['cantidad_joaquin'] = 0
    
    # Crear estimación para la combinación Joaquín Rodríguez
    merged_combinacion = merged_rodriguez.copy()
    
    # Si tenemos una estimación global, la distribuimos proporcionalmente según apellido Rodríguez
    if estimacion_joaquin_rodriguez > 0:
        total_rodriguez = merged_rodriguez['cantidad'].sum()
        if total_rodriguez > 0:
            merged_combinacion['estimacion_joaquin_rodriguez'] = (
                merged_rodriguez['cantidad'] / total_rodriguez * estimacion_joaquin_rodriguez
            )
        else:
            merged_combinacion['estimacion_joaquin_rodriguez'] = 0
    else:
        # Si no tenemos estimación global, hacemos una aproximación basada en los datos disponibles
        merged_combinacion['estimacion_joaquin_rodriguez'] = merged_rodriguez['cantidad'] * 0.01
    
    # Convertir a GeoJSON para Bokeh
    geo_source_rodriguez = GeoJSONDataSource(geojson=merged_rodriguez.to_json())
    geo_source_joaquin = GeoJSONDataSource(geojson=merged_joaquin.to_json())
    geo_source_combinacion = GeoJSONDataSource(geojson=merged_combinacion.to_json())
    
    # Configurar colores para los mapas
    palette_rodriguez = Viridis256
    color_mapper_rodriguez = LinearColorMapper(
        palette=palette_rodriguez, 
        low=merged_rodriguez['cantidad'].min(),
        high=merged_rodriguez['cantidad'].max()
    )
    
    # Crear figura
    figure_width = 700
    figure_height = 600
    
    p1 = figure(
        title="Distribución del apellido Rodríguez por provincia",
        height=figure_height, 
        width=figure_width, 
        toolbar_location="right"
    )
    
    # Añadir los polígonos de las provincias
    p1.patches(
        'xs', 'ys', 
        source=geo_source_rodriguez,
        fill_color={'field': 'cantidad', 'transform': color_mapper_rodriguez},
        line_color='black', 
        line_width=0.5, 
        fill_alpha=0.7
    )
    
    # Añadir la barra de color
    color_bar_rodriguez = ColorBar(
        color_mapper=color_mapper_rodriguez, 
        label_standoff=12, 
        border_line_color=None,
        location=(0, 0), 
        title='Cantidad de personas'
    )
    p1.add_layout(color_bar_rodriguez, 'right')
    
    # Añadir información al pasar el cursor
    hover_rodriguez = HoverTool(tooltips=[
        ('Provincia', '@provincia_nombre'),
        ('Cantidad', '@cantidad{0,0}')
    ])
    p1.add_tools(hover_rodriguez)
    
    # Guardar el mapa
    output_file("visualizaciones/mapa_rodriguez_provincias.html")
    save(p1)
    print("Mapa de apellido Rodríguez guardado en visualizaciones/mapa_rodriguez_provincias.html")
    
    return "Mapa generado correctamente basado en datos reales."


generar_mapa_distribucion_argentina()