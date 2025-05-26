import pandas as pd
from bokeh.plotting import figure, output_file, save
from bokeh.models import (HoverTool, ColumnDataSource, Span, Label,
                         LabelSet, ColorBar, LinearColorMapper,NumeralTickFormatter)
from bokeh.layouts import column, row, gridplot
from bokeh.transform import factor_cmap, transform, linear_cmap
from bokeh.palettes import Viridis256, RdYlGn
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

# Buscar el apellido Rodriguez
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

# Buscar el nombre Joaquin
joaquin_historico = historico_nombres[historico_nombres['nombre'].str.lower() == 'joaquin']
if len(joaquin_historico) == 0:
    joaquin_historico = historico_nombres[historico_nombres['nombre'].str.lower() == 'joaquín']

# Imprimir las columnas de joaquin_historico para verificar
print("Columnas de joaquin_historico:", joaquin_historico.columns)

# Chequeo de que la columna 'provincia_nombre' existe
if 'provincia_nombre' in joaquin_historico.columns:


# Creacion de un DataFrame que contenga la cantidad de 'Joaquin' por provincia
    joaquin_por_provincia = joaquin_historico.groupby('provincia_nombre')['cantidad'].sum().reset_index()
    joaquin_por_provincia.rename(columns={'cantidad': 'cantidad_joaquin'}, inplace=True)
else:
    print("Error: 'provincia_nombre' no se encuentra en joaquin_historico.")
    joaquin_por_provincia = pd.DataFrame(columns=['provincia_nombre', 'cantidad_joaquin'])

# Combinar este DataFrame con rodriguez_provincias
rodriguez_provincias = rodriguez_provincias.merge(joaquin_por_provincia, on='provincia_nombre', how='left')

# Ordenar datos históricos por año
if 'anio' in joaquin_historico.columns:
    joaquin_historico = joaquin_historico.sort_values('anio')
    
# Imprimir información básica para verificar
print(f"\nDatos de apellido Rodríguez a nivel país: {len(rodriguez_pais)} registros")
print(f"Datos de apellido Rodríguez por provincia: {len(rodriguez_provincias)} registros")
print(f"Datos de ranking de Rodríguez por provincia: {len(rodriguez_ranking_provincias)} registros")
print(f"Datos históricos del nombre Joaquín: {len(joaquin_historico)} registros")



#En este punto, los DataFrames rodriguez_pais, rodriguez_provincias y joaquin_historico están preparados para su análisis. Se pueden utilizar en las siguientes funciones para generar visualizaciones y análisis específicos.


# --------------------------------------
# 1. Posicionamiento nacional del apellido Rodríguez
# --------------------------------------

def analizar_posicionamiento_nacional():
    print("\n1. Analizando posicionamiento nacional del apellido Rodríguez...")
    
    if len(rodriguez_pais) == 0:
        print("No se encontraron datos del apellido Rodríguez a nivel nacional")
        return "No hay datos suficientes para el análisis de posicionamiento nacional"
    
    # Datos del posicionamiento
    ranking = rodriguez_pais['ranking'].values[0]
    porcentaje = rodriguez_pais['porcentaje_de_poblacion_portadora'].values[0]
    
    # Crear visualización
    top_apellidos = apellidos_pais.sort_values('ranking').head(20)
    
    # Crear colores para destacar Rodriguez
    colors = ['#C70039' if apellido.lower() in ['rodriguez', 'rodríguez'] else '#1F77B4' 
              for apellido in top_apellidos['apellido']]
    
    # Agregar colores al ColumnDataSource
    top_apellidos['color'] = colors

    # Redondear los porcentajes a dos decimales
    top_apellidos['porcentaje_de_poblacion_portadora'] = top_apellidos['porcentaje_de_poblacion_portadora'].round(2)

    source = ColumnDataSource(top_apellidos)
    
    p = figure(y_range=top_apellidos['apellido'], width=1200, height=800,
              title="Top 20 Apellidos + Comunes en Argentina",
              toolbar_location="right", sizing_mode="fixed")
    
    # Configurar el título
    p.title.text_font_size = "18pt"  
    p.title.align = "center"        
    p.title.border_line_dash_offset = 10

    # Calcular el rango del eje X con un margen adicional
    max_porcentaje = top_apellidos['porcentaje_de_poblacion_portadora'].max()
    p.x_range.end = max_porcentaje * 1.1  # Agregar un 10% de margen al rango máximo

    # Ajustar el rango del eje Y para agregar un margen superior
    p.y_range.range_padding = 0.1

    # Aumentar el tamaño de los apellidos en el eje Y
    p.yaxis.major_label_text_font_size = "14pt"

    # Crear barras
    bars = p.hbar(y='apellido', right='porcentaje_de_poblacion_portadora', 
                 source=source, height=0.8, color='color')
    
    # Añadir etiquetas de porcentaje
    labels = LabelSet(x='porcentaje_de_poblacion_portadora', y='apellido', 
                     text='porcentaje_de_poblacion_portadora', level='glyph',
                     x_offset=10,
                     y_offset=-5,
                     source=source, 
                     text_font_size='14pt')
    
    p.add_layout(labels)
    
    # Configuración del gráfico
    p.xaxis.axis_label = "Porcentaje de la Población (%)"
    p.xaxis.axis_label_text_font_size = "15pt" 
    p.xaxis.major_label_text_font_size = "13pt"  
    p.xgrid.grid_line_color = None
    
    # Añadir información interactiva
    hover = HoverTool()
    hover.tooltips = [
        ("Apellido", "@apellido"),
        ("Ranking", "@ranking"),
        ("Porcentaje", "@porcentaje_de_poblacion_portadora%")
    ]
    p.add_tools(hover)
    
    # Guardar y mostrar
    output_file("visualizaciones/rodriguez_ranking_nacional.html")
    save(p)
    print(f"Gráfico guardado en visualizaciones/rodriguez_ranking_nacional.html")
    
    return f"El apellido Rodríguez ocupa el puesto {ranking} a nivel nacional, " \
           f"siendo portado por aproximadamente el {porcentaje}% de la población argentina."



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
    
    # Crear gráfico de barras
    p = figure(x_range=provincias_ordenadas['provincia_nombre'], 
               width=1200, height=600,
               title="Distribución del Apellido Rodríguez por Provincia",
               toolbar_location="right",
               title_location="above")
    
    # Ajustar el título
    p.title.text_font_size = "20pt"  
    p.title.standoff = 20  
    p.title.align = "center"
    
    # Ajustar títulos de los ejes
    p.xaxis.axis_label = "Provincia"
    p.yaxis.axis_label = "Cantidad de personas (en miles)"  
    p.yaxis.axis_label_standoff = 15 
    p.xaxis.axis_label_text_font_size = "16pt"  
    p.yaxis.axis_label_text_font_size = "16pt"
    
    # Crear barras usando la nueva columna de colores
    p.vbar(x='provincia_nombre', top='cantidad_miles', width=0.8, source=source,
           fill_color='color')
    
    # Configuración del gráfico
    p.xaxis.major_label_orientation = 3.14/4  
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

# --------------------------------------
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
    combined['color'] = colores

    # Crear gráfico
    source = ColumnDataSource(combined)
    
    p = figure(y_range=combined['provincia_nombre'], width=800, height=400,
              title="Provincias con Mayor y Menor Presencia del Apellido Rodríguez",
              toolbar_location="right")
    
    # Ajustar el título
    p.title.text_font_size = "12pt"  #
    p.title.standoff = 20  # 
    p.title.align = "center"  
    
    # Crear barras
    bars = p.hbar(y='provincia_nombre', right='cantidad', height=0.8, 
                  source=source, color='color')  # Usar la columna 'color'
    
    # Configuración del eje X
    p.xaxis.axis_label = "Cantidad de personas"
    p.xaxis.axis_label_text_font_size = "12pt"
    p.xaxis.axis_label_text_font_style = "bold"
    p.xaxis.axis_label_standoff = 15
    p.xgrid.grid_line_color = None
    
    # Ajustar el rango del eje X para que el cero coincida con el eje Y
    p.x_range.start = 0
    p.x_range.end = combined['cantidad'].max() * 1.1

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
    provincias['color'] = ['#FF5733' if es_cordoba else '#1F77B4' for es_cordoba in provincias['es_cordoba']]
    
    source = ColumnDataSource(provincias)
    
    p = figure(x_range=provincias['provincia_nombre'], width=900, height=500,
               title="Comparativa: Rodríguez en Córdoba vs Otras Provincias",
               toolbar_location="right", x_axis_label="Provincia", 
               y_axis_label="Cantidad de personas")
    
    # Usar la columna de colores
    p.vbar(x='provincia_nombre', top='cantidad', width=0.8, source=source, 
          fill_color='color', line_color='white')
    
    # Rotar etiquetas del eje X
    p.xaxis.major_label_orientation = 3.14/4
    
    # Línea para el promedio nacional
    prom_line = Span(location=promedio_nacional, 
                    dimension='width', line_color='red', 
                    line_dash='dashed', line_width=2)
    p.add_layout(prom_line)
    
    # Etiqueta para la línea del promedio
    label = Label(x=5, y=promedio_nacional+500, 
                 text=f"Promedio Nacional: {promedio_nacional:.0f}",
                 text_color='red')
    p.add_layout(label)
    
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

# --------------------------------------
# 5. Evolución histórica del nombre Joaquín
# --------------------------------------

def analizar_evolucion_historica():
    print("\n6. Analizando evolución histórica del nombre Joaquín...")
    
    if len(joaquin_historico) == 0:
        print("No se encontraron datos históricos del nombre Joaquín")
        return "No hay datos suficientes para el análisis de evolución histórica"
    
    # Agrupar por año y sumar
    joaquin_por_anio = joaquin_historico.groupby('anio')['cantidad'].sum().reset_index()
    
    # Crear gráfico interactivo
    source = ColumnDataSource(joaquin_por_anio)
    
    p = figure(width=1080, height=600, 
              title="Evolución Histórica del Nombre Joaquín",
              title_location="above",
              x_axis_label="Año", y_axis_label="Cantidad de Nacimientos",
              toolbar_location="right")
    
    # Ajustar el tamaño de la fuente del título
    p.title.text_font_size = "18pt"
    p.title.standoff = 20 
    p.title.align = "center"

    # Ajustar el tamaño y el estilo de los ejes

    p.yaxis.axis_label_text_font_size = "14pt"
    p.yaxis.axis_label_text_font_style = "bold"
    p.yaxis.axis_label_standoff = 15


    p.xaxis.axis_label_text_font_size = "12pt"
    p.xaxis.axis_label_text_font_style = "bold"
    p.xaxis.axis_label_standoff = 15
   
   

    # Línea de tendencia
    line = p.line('anio', 'cantidad', source=source, line_width=2, 
                 line_color='#1F77B4')
    
    # Añadir marcadores
    circles = p.circle('anio', 'cantidad', source=source, size=8, 
                      color='#C70039', fill_alpha=0.4)
    
    # Agregar información interactiva
    hover = HoverTool(renderers=[circles], tooltips=[
        ("Año", "@anio"),
        ("Nacimientos", "@cantidad")
    ])
    p.add_tools(hover)
    
    
    # Guardar y mostrar
    output_file("visualizaciones/joaquin_evolucion_historica.html")
    save(p)
    print(f"Gráfico guardado en visualizaciones/joaquin_evolucion_historica.html")
    
    # Calcular y imprimir algunos insights
    anio_min = joaquin_por_anio['anio'].min()
    anio_max = joaquin_por_anio['anio'].max()
    cantidad_min = joaquin_por_anio['cantidad'].min()
    cantidad_max = joaquin_por_anio['cantidad'].max()

    
# --------------------------------------
# 6. Picos de popularidad del nombre Joaquin
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
              title_location="above",
              x_axis_label="Año", y_axis_label="Cantidad de Nacimientos",
              toolbar_location="right")
    
    # Ajustar el título
    p.title.text_font_size = "18pt"
    p.title.standoff = 20  
    p.title.align = "center"

     #Ajustar ejes

    p.yaxis.axis_label_text_font_size = "14pt"
    p.yaxis.axis_label_text_font_style = "bold"
    p.yaxis.axis_label_standoff = 15

    p.xaxis.axis_label_text_font_size = "12pt"
    p.xaxis.axis_label_text_font_style = "bold"
    p.xaxis.axis_label_standoff = 15
    
    # Añadir un punto destacado para mi nacimiento
    fecha_nacimiento = 1991 
    nacimiento_cantidad = joaquin_por_anio[joaquin_por_anio['anio'] == fecha_nacimiento]['cantidad'].sum()

    # Crear un DataFrame para el punto destacado
    nacimiento_data = pd.DataFrame({
        'anio': [fecha_nacimiento],
        'cantidad': [nacimiento_cantidad],
        'cambio_porcentual': [None]
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
                                 color='blue', legend_label="Nacimiento Joaquin Rodriguez", 
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
        ("Análisis", "Mi nacimiento se da entre periodos de popularidad del nombre Joaquin.")
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

# --------------------------------------
# 7. Comparativa generacional del nombre Joaquín
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
        # Filtrar datos para mi generación
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
    
    # Ajustar título
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

    # Barras para total con intercalación de colores
    p.vbar(x='generacion', top='total', width=0.6, source=source,
           color='color', legend_label="Total Nacimientos")
    
    # Configuración
    p.xaxis.major_label_orientation = 3.14/4
    p.yaxis.axis_label = "Total de Nacimientos"
    p.yaxis.axis_label_text_font_size = "14pt" 
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

# --------------------------------------
# 8. Unicidad de la combinación Joaquín Rodríguez
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

# --------------------------------------
# 9. Generar mapa interactivo de distribución
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
    
    # Asegúrate de que la columna 'provincia_nombre' esté en merged_rodriguez
    if 'provincia_nombre' not in merged_rodriguez.columns:
        merged_rodriguez['provincia_nombre'] = merged_rodriguez['provincia_norm']  # O la columna que corresponda

    # Convertir a GeoJSON para Bokeh
    geo_source_rodriguez = GeoJSONDataSource(geojson=merged_rodriguez.to_json())
    geo_source_joaquin = GeoJSONDataSource(geojson=merged_joaquin.to_json())
    geo_source_combinacion = GeoJSONDataSource(geojson=merged_combinacion.to_json())
    
    # Configurar colores para los mapas
    palette_rodriguez = RdYlGn[9]  # Usar la paleta de rojo a verde con 9 colores
    
    # Ajustar los valores de la escala de colores
    low_value = merged_rodriguez['cantidad'].quantile(0.1)  # 10% del mínimo
    high_value = merged_rodriguez['cantidad'].quantile(0.9)  # 90% del máximo
    
    color_mapper_rodriguez = LinearColorMapper(
        palette=palette_rodriguez, 
        low=low_value,
        high=high_value
    )
    
    # Aumentar el tamaño de la figura en un 20% y hacerla un poco más larga para mantener la figura correcta del mapa
    figure_width = 720
    figure_height = 880
    
    p1 = figure(
        title="Distribución del apellido Rodríguez por provincia",
        height=figure_height, 
        width=figure_width, 
        toolbar_location="right"
    )
    
    # Configurar el título
    p1.title.text_font_size = "18pt"  # Aumentar el tamaño del título
    p1.title.standoff = 20  # Aumentar el standoff del título
    p1.title.align = "center"  # Centrar el título
    
    # Añadir los polígonos de las provincias
    p1.patches(
        'xs', 'ys', 
        source=geo_source_rodriguez,
        fill_color={'field': 'cantidad', 'transform': color_mapper_rodriguez},
        line_color='black', 
        line_width=0.5, 
        fill_alpha=0.7
    )
    
    # Ocultar los ejes X e Y
    p1.xaxis.visible = False
    p1.yaxis.visible = False
    
    # Ocultar la cuadrícula del fondo
    p1.xgrid.visible = False
    p1.ygrid.visible = False
    
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


# Llamadas a las funciones
print(analizar_posicionamiento_nacional())
print(crear_mapa_distribucion())
print(comparar_provincias())
print(analizar_cordoba())
print(analizar_evolucion_historica())
print(identificar_picos_popularidad())
print(analizar_generaciones())
print(estimar_unicidad_combinacion())
print(generar_mapa_distribucion_argentina())