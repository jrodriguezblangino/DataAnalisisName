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
# 7. Picos de popularidad del nombre Joaquín
# --------------------------------------

def identificar_picos_popularidad():
    print("\n7. Identificando picos de popularidad del nombre Joaquín...")
    
    if len(joaquin_historico) == 0:
        print("No se encontraron datos históricos del nombre Joaquín")
        return "No hay datos suficientes para identificar picos de popularidad"
    
    # Identificar cambios significativos en la popularidad
    joaquin_por_anio = joaquin_historico.groupby('anio')['cantidad'].sum().reset_index()
    
    # Calcular el cambio porcentual respecto al año anterior
    joaquin_por_anio['cambio_porcentual'] = joaquin_por_anio['cantidad'].pct_change() * 100
    
    # Identificar picos (definidos como años donde el crecimiento fue superior al 15%)
    picos = joaquin_por_anio[joaquin_por_anio['cambio_porcentual'] > 15].copy()
    
    # Identificar caídas (definidas como años donde el decrecimiento fue superior al 15%)
    caidas = joaquin_por_anio[joaquin_por_anio['cambio_porcentual'] < -15].copy()
    
    # Crear visualización de picos y caídas
    source_completo = ColumnDataSource(joaquin_por_anio)
    source_picos = ColumnDataSource(picos)
    source_caidas = ColumnDataSource(caidas)
    
    p = figure(width=1080, height=600, 
              title="Picos y Caídas en la Popularidad del Nombre Joaquín",
              title_location= "above",
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

       #Ajustar el tamaño y el estilo del eje x

    p.xaxis.axis_label_text_font_size = "12pt"
    p.xaxis.axis_label_text_font_style = "bold"
    p.xaxis.axis_label_standoff = 15
    
    # Añadir un punto destacado para el nacimiento el 16 de julio de 1991
    fecha_nacimiento = 1991  # Año de nacimiento
    nacimiento_cantidad = joaquin_por_anio[joaquin_por_anio['anio'] == fecha_nacimiento]['cantidad'].sum()

    # Crear un DataFrame para el punto destacado
    nacimiento_data = pd.DataFrame({
        'anio': [fecha_nacimiento],
        'cantidad': [nacimiento_cantidad],
        'cambio_porcentual': [None]  # No se necesita para el punto destacado
    })

    # Crear un ColumnDataSource para el nacimiento
    source_nacimiento = ColumnDataSource(nacimiento_data)

    # Gráfico base de evolución
    line = p.line('anio', 'cantidad', source=source_completo, line_width=2, 
                  line_color='gray', legend_label="Tendencia")
    
    # Destacar picos
    picos_puntos = p.circle('anio', 'cantidad', source=source_picos, size=10, 
                             color='green', legend_label="Picos de Popularidad")
    
    # Destacar caídas
    caidas_puntos = p.circle('anio', 'cantidad', source=source_caidas, size=10, 
                              color='red', legend_label="Caídas de Popularidad")
    
    # Destacar el nacimiento
    nacimiento_punto = p.circle('anio', 'cantidad', source=source_nacimiento, size=12, 
                                 color='blue', legend_label="Nacimiento (16 de Julio 1991)", 
                                 line_color='black', line_width=2)
    
    # Añadir información interactiva para los picos
    hover_picos = HoverTool(renderers=[picos_puntos], tooltips=[
        ("Año", "@anio"),
        ("Nacimientos", "@cantidad"),
        ("Crecimiento", "@cambio_porcentual{0.0}%")
    ])
    p.add_tools(hover_picos)

    # Añadir información interactiva para las caídas
    hover_caidas = HoverTool(renderers=[caidas_puntos], tooltips=[
        ("Año", "@anio"),
        ("Nacimientos", "@cantidad"),
        ("Decrecimiento", "@cambio_porcentual{0.0}%")
    ])
    p.add_tools(hover_caidas)

    # Añadir información interactiva para el nacimiento
    hover_nacimiento = HoverTool(renderers=[nacimiento_punto], tooltips=[
        ("Año", "@anio"),
        ("Nacimientos", "@cantidad"),
        ("Análisis", "Tu nacimiento se da entre periodos de popularidad del nombre Joaquín.")
    ])
    p.add_tools(hover_nacimiento)
    
    # Configuración
    p.legend.location = "top_left"
    p.legend.click_policy = "hide"
    
    # Guardar y mostrar
    output_file("visualizaciones/joaquin_picos_popularidad.html")
    save(p)
    print(f"Gráfico guardado en visualizaciones/joaquin_picos_popularidad.html")
    
    # Generar insights
    if len(picos) > 0:
        mayor_pico = picos.loc[picos['cambio_porcentual'].idxmax()]
        pico_info = f"El mayor pico de popularidad ocurrió en {int(mayor_pico['anio'])}, "\
                   f"con un aumento del {mayor_pico['cambio_porcentual']:.1f}% "\
                   f"respecto al año anterior."
    else:
        pico_info = "No se identificaron picos significativos de popularidad."
    
    if len(caidas) > 0:
        mayor_caida = caidas.loc[caidas['cambio_porcentual'].idxmin()]
        caida_info = f"La mayor caída ocurrió en {int(mayor_caida['anio'])}, "\
                    f"con una disminución del {abs(mayor_caida['cambio_porcentual']):.1f}% "\
                    f"respecto al año anterior."
    else:
        caida_info = "No se identificaron caídas significativas de popularidad."
    
    return f"{pico_info} {caida_info}"

identificar_picos_popularidad()