# Joaquín Rodríguez: Análisis de Datos en Argentina
# Proyecto Portfolio Analista de Datos

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from bokeh.plotting import figure, show, output_file, save
from bokeh.io import output_notebook, show
from bokeh.models import (GeoJSONDataSource, LinearColorMapper, ColorBar, 
                         HoverTool, ColumnDataSource, Span, Label,
                         LabelSet, Legend, Range1d)
from bokeh.palettes import Viridis256, Category20c
from bokeh.layouts import column, row, gridplot
from bokeh.transform import factor_cmap
import geopandas as gpd
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
import warnings
import os
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

# Ordenar datos históricos por año
if 'anio' in joaquin_historico.columns:
    joaquin_historico = joaquin_historico.sort_values('anio')
    
# Imprimir información básica para verificar
print(f"\nDatos de apellido Rodríguez a nivel país: {len(rodriguez_pais)} registros")
print(f"Datos de apellido Rodríguez por provincia: {len(rodriguez_provincias)} registros")
print(f"Datos de ranking de Rodríguez por provincia: {len(rodriguez_ranking_provincias)} registros")
print(f"Datos históricos del nombre Joaquín: {len(joaquin_historico)} registros")

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
    
    # Crear visualización Bokeh
    top_apellidos = apellidos_pais.sort_values('ranking').head(20)
    
    # Crear colores para destacar Rodríguez
    colors = ['#C70039' if apellido.lower() in ['rodriguez', 'rodríguez'] else '#1F77B4' 
              for apellido in top_apellidos['apellido']]
    
    # Agregar colores al ColumnDataSource
    top_apellidos['color'] = colors
    source = ColumnDataSource(top_apellidos)
    
    p = figure(y_range=top_apellidos['apellido'], width=800, height=500,
              title="Top 20 Apellidos más Comunes en Argentina",
              toolbar_location="right")
    
    # Crear barras
    bars = p.hbar(y='apellido', right='porcentaje_de_poblacion_portadora', 
                 source=source, height=0.8, color='color')  # Usar la columna 'color'
    
    # Añadir etiquetas de porcentaje
    labels = LabelSet(x='porcentaje_de_poblacion_portadora', y='apellido', 
                     text='porcentaje_de_poblacion_portadora', level='glyph',
                     x_offset=5, y_offset=0, source=source, 
                     text_font_size='8pt')
    
    p.add_layout(labels)
    
    # Configuración del gráfico
    p.xaxis.axis_label = "Porcentaje de la Población (%)"
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
    
    source = ColumnDataSource(provincias_ordenadas)
    
    # Crear gráfico de barras
    p = figure(x_range=provincias_ordenadas['provincia_nombre'], 
               width=900, height=500,
               title="Distribución del Apellido Rodríguez por Provincia",
               toolbar_location="right",
               x_axis_label="Provincia", 
               y_axis_label="Cantidad de personas")
    
    # Crear barras
    p.vbar(x='provincia_nombre', top='cantidad', width=0.8, source=source,
           color="#1F77B4")
    
    # Configuración del gráfico
    p.xaxis.major_label_orientation = 3.14/4  # Rotar etiquetas del eje X
    
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
    total_personas = provincias_ordenadas['cantidad'].sum()
    max_provincia = provincias_ordenadas.iloc[0]['provincia_nombre']
    max_cantidad = provincias_ordenadas.iloc[0]['cantidad']
    
    return f"En total hay {total_personas} personas con el apellido Rodríguez en Argentina. " \
           f"La mayor concentración se encuentra en {max_provincia} con {max_cantidad} personas."

# --------------------------------------
# 3. Comparativa entre provincias
# --------------------------------------

def comparar_provincias():
    print("\n3. Comparando presencia del apellido Rodríguez entre provincias...")
    
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
    colores = ['#FF7F0E'] * 5 + ['#1F77B4'] * 5
    combined['color'] = colores  # Agregar la columna de colores
    
    # Crear gráfico
    source = ColumnDataSource(combined)
    
    p = figure(y_range=combined['provincia_nombre'], width=800, height=400,
              title="Provincias con Mayor y Menor Presencia del Apellido Rodríguez",
              toolbar_location="right")
    
    # Crear barras
    bars = p.hbar(y='provincia_nombre', right='cantidad', height=0.8, 
                  source=source, color='color')  # Usar la columna 'color'
    
    # Añadir etiquetas
    labels = LabelSet(x='cantidad', y='provincia_nombre', text='cantidad', 
                     source=source, x_offset=5, text_font_size='8pt')
    p.add_layout(labels)
    
    # Configuración
    p.xaxis.axis_label = "Cantidad de personas"
    p.xgrid.grid_line_color = None
    
    # Información interactiva
    hover = HoverTool()
    hover.tooltips = [
        ("Provincia", "@provincia_nombre"),
        ("Cantidad", "@cantidad personas")
    ]
    p.add_tools(hover)
    
    # Guardar y mostrar
    output_file("visualizaciones/rodriguez_comparativa_provincias.html")
    save(p)
    print(f"Gráfico guardado en visualizaciones/rodriguez_comparativa_provincias.html")
    
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
    
    p = figure(width=900, height=500, 
              title="Evolución Histórica del Nombre Joaquín",
              x_axis_label="Año", y_axis_label="Cantidad de Nacimientos",
              toolbar_location="right")
    
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
    anio_popular = joaquin_por_anio.loc[joaquin_por_anio['cantidad'].idxmax(), 'anio']
    
    return f"El nombre Joaquín tiene registros desde {anio_min} hasta {anio_max}. "\
           f"Su popularidad varió desde un mínimo de {cantidad_min} nacimientos hasta "\
           f"un máximo de {cantidad_max} nacimientos en el año {anio_popular}."

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
    
    p = figure(width=900, height=500, 
              title="Picos y Caídas en la Popularidad del Nombre Joaquín",
              x_axis_label="Año", y_axis_label="Cantidad de Nacimientos",
              toolbar_location="right")
    
    # Gráfico base de evolución
    line = p.line('anio', 'cantidad', source=source_completo, line_width=2, 
                 line_color='gray', legend_label="Tendencia")
    
    # Destacar picos
    picos_puntos = p.circle('anio', 'cantidad', source=source_picos, size=10, 
                          color='green', legend_label="Picos de Popularidad")
    
    # Destacar caídas
    caidas_puntos = p.circle('anio', 'cantidad', source=source_caidas, size=10, 
                           color='red', legend_label="Caídas de Popularidad")
    
    # Añadir información interactiva
    hover_picos = HoverTool(renderers=[picos_puntos], tooltips=[
        ("Año", "@anio"),
        ("Nacimientos", "@cantidad"),
        ("Crecimiento", "@cambio_porcentual{0.0}%")
    ])
    
    hover_caidas = HoverTool(renderers=[caidas_puntos], tooltips=[
        ("Año", "@anio"),
        ("Nacimientos", "@cantidad"),
        ("Decrecimiento", "@cambio_porcentual{0.0}%")
    ])
    
    p.add_tools(hover_picos, hover_caidas)
    
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
# 9. Comparativa generacional del nombre Joaquín
# --------------------------------------

def analizar_generaciones():
    print("\n9. Analizando popularidad del nombre Joaquín por generaciones...")
    
    if len(joaquin_historico) == 0:
        print("No se encontraron datos históricos del nombre Joaquín")
        return "No hay datos suficientes para el análisis generacional"
    
    # Definir rangos generacionales (aproximados)
    generaciones = {
        'Silenciosa (1928-1945)': (1928, 1945),
        'Baby Boomers (1946-1964)': (1946, 1964),
        'Generación X (1965-1980)': (1965, 1980),
        'Millennials (1981-1996)': (1981, 1996),
        'Generación Z (1997-2012)': (1997, 2012),
        'Generación Alpha (2013-)': (2013, 2030)
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
    
    if len(df_generaciones) == 0:
        return "No hay datos suficientes para realizar el análisis generacional"
    
    # Crear visualización
    source = ColumnDataSource(df_generaciones)
    
    p = figure(x_range=df_generaciones['generacion'], width=800, height=500,
              title="Popularidad del Nombre Joaquín por Generación",
              toolbar_location="right")
    
    # Barras para total
    p.vbar(x='generacion', top='total', width=0.6, source=source,
          color="#1F77B4", legend_label="Total Nacimientos")
    
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

# --------------------------------------
# 10. Unicidad de la combinación Joaquín Rodríguez
# --------------------------------------

def estimar_unicidad_combinacion():
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
    colores = ["#1F77B4", "#FF7F0E", "#2CA02C"]
    
    source = ColumnDataSource(data=dict(labels=labels, valores=valores, colores=colores))
    
    p = figure(x_range=labels, width=600, height=500,
               title="Estimación de Personas con el Nombre y Apellido",
               toolbar_location="right")  # Cambiar a escala lineal
    
    p.vbar(x='labels', top='valores', width=0.6, source=source,
           color='colores')  # Usar la columna de colores
    
    p.y_range.start = 1  # Comenzar desde 1 en escala lineal
    p.xgrid.grid_line_color = None
    p.yaxis.axis_label = "Estimación de Personas"
    p.xaxis.major_label_orientation = 3.14/4
    
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

# Llamadas a las funciones
print(analizar_posicionamiento_nacional())
print(crear_mapa_distribucion())
print(comparar_provincias())
print(analizar_cordoba())
print(analizar_evolucion_historica())
print(identificar_picos_popularidad())
print(analizar_generaciones())
print(estimar_unicidad_combinacion())  