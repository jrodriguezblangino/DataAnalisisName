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

def analizar_cordoba():
    print("\n4. Analizando presencia del apellido Rodríguez en Córdoba...")
    
    # Obtener datos de Córdoba
    cordoba_datos = rodriguez_provincias[rodriguez_provincias['provincia_nombre'].str.lower() == 'córdoba']
    if len(cordoba_datos) == 0:
        cordoba_datos = rodriguez_provincias[rodriguez_provincias['provincia_nombre'].str.lower() == 'cordoba']
    
    if len(cordoba_datos) == 0:
        print("No se encontraron datos para Córdoba")
        return "No se encontraron datos para Córdoba"
    
    cantidad_cordoba = cordoba_datos['cantidad'].values[0]
    
    # Obtener ranking en Córdoba
    cordoba_ranking = rodriguez_ranking_provincias[
        rodriguez_ranking_provincias['provincia_nombre'].str.lower() == 'córdoba'
    ]
    if len(cordoba_ranking) == 0:
        cordoba_ranking = rodriguez_ranking_provincias[
            rodriguez_ranking_provincias['provincia_nombre'].str.lower() == 'cordoba'
        ]
    
    if len(cordoba_ranking) == 0:
        ranking_texto = "No se encontró información de ranking para Córdoba"
    else:
        ranking_cordoba = cordoba_ranking['ranking'].values[0]
        porcentaje_cordoba = cordoba_ranking['porcentaje_poblacion_portadora'].values[0]
        ranking_texto = f"En Córdoba, Rodríguez ocupa el puesto {ranking_cordoba} con un {porcentaje_cordoba}% de la población"
    
    # Comparar con el promedio nacional
    promedio_nacional = rodriguez_provincias['cantidad'].mean()
    ratio = cantidad_cordoba / promedio_nacional
    
    # Crear visualización comparativa
    provincias = rodriguez_provincias.drop_duplicates(subset='provincia_nombre').copy()
    provincias['es_cordoba'] = provincias['provincia_nombre'].str.lower().isin(['córdoba', 'cordoba'])
    provincias = provincias.sort_values('cantidad', ascending=False)
    
    # Crear colores para las barras
    provincias['color'] = ['#C70039' if es_cordoba else '#1F77B4' for es_cordoba in provincias['es_cordoba']]
    
    source = ColumnDataSource(provincias)
    
    p = figure(x_range=provincias['provincia_nombre'], width=1200, height=800,
               title="Comparativa: Rodríguez en Córdoba vs Otras Provincias",
               toolbar_location="right", x_axis_label="Provincia", 
               y_axis_label="Cantidad de personas (en miles)")
    
    # Usar la columna de colores
    p.vbar(x='provincia_nombre', top='cantidad', width=0.8, source=source, 
          fill_color='color', line_color='white')
    
    # Rotar etiquetas del eje X
    p.xaxis.major_label_orientation = 3.14/4
    
    # Configurar título del eje X para que aparezca más grande y en negrita
    p.xaxis.axis_label_text_font_size = "15pt"
    p.xaxis.axis_label_text_font_style = "bold"
    
    # Línea para el promedio nacional
    prom_line = Span(location=promedio_nacional, 
                    dimension='width', line_color='red', 
                    line_dash='dashed', line_width=1)
    p.add_layout(prom_line)
    
    # Etiqueta para la línea del promedio
    label = Label(x=p.x_range.end + 1.6,  # Mover el label más a la derecha
                 y=round(promedio_nacional) + 80,  # Aumentar el desplazamiento
                 text=f"Promedio Nacional: {round(promedio_nacional)} personas",  # Redondear
                 text_color='red', 
                 background_fill_color='white',
                 background_fill_alpha=0.7,
                 x_offset=0,  # Ajuste para centrar el texto horizontalmente
                 y_offset=30  # Aumentar el ajuste para despegar más la etiqueta
                 )
    p.add_layout(label)
    
    # Configuración del eje Y
    p.yaxis.formatter.use_scientific = False
    p.yaxis.axis_label = "Cantidad de personas (en miles)"  # Ajustar el padding para despegar el etiqueta
    p.yaxis.axis_label_text_font_size = "15pt"
    p.yaxis.axis_label_text_font_style = "bold"
    p.yaxis.axis_label_standoff = 10  # Añadir un espacio entre el eje y la etiqueta para despegar
    p.yaxis.major_label_text_font_size = "13pt"
    
    # Aumentar tamaño del título
    p.title.text_font_size = "18pt"
    p.title.align = "center"
    
    # Eliminar cuadrícula de fondo
    p.xgrid.visible = False
    p.ygrid.visible = False
    
    # Información interactiva
    hover = HoverTool()
    hover.tooltips = [
        ("Provincia", "@provincia_nombre"),
        ("Cantidad", "@cantidad personas"),
    ]
    p.add_tools(hover)
    
    # Guardar y mostrar
    output_file("visualizaciones/rodriguez_analisis_cordoba.html")
    save(p)
    print(f"Gráfico guardado en visualizaciones/rodriguez_analisis_cordoba.html")
    
    return f"En Córdoba hay {cantidad_cordoba} personas con el apellido Rodríguez. "\
           f"Esto es {ratio:.2f} veces el promedio nacional de {promedio_nacional:.0f} personas por provincia. "\
           f"{ranking_texto}."


analizar_cordoba()
