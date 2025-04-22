import pandas as pd
import geopandas as gpd
from bokeh.plotting import figure, output_file, save
from bokeh.models import GeoJSONDataSource, LinearColorMapper, ColorBar, HoverTool, ColumnDataSource, Select, CustomJS
from bokeh.palettes import Viridis256, RdYlBu11, Turbo256
from bokeh.layouts import column, row
from bokeh.io import reset_output

def generar_mapa_distribucion_argentina(rodriguez_provincias, joaquin_por_provincia, estimacion_global=0):
    """
    Genera un mapa de calor de Argentina con la distribución de Rodríguez, Joaquín y la combinación.
    
    Parámetros:
    ----------
    rodriguez_provincias : DataFrame
        DataFrame con la cantidad de personas con apellido Rodríguez por provincia
    joaquin_por_provincia : DataFrame
        DataFrame con la cantidad de personas con nombre Joaquín por provincia
    estimacion_global : float, opcional
        Estimación global de personas con la combinación Joaquín Rodríguez
        
    Retorna:
    --------
    str
        Mensaje con la ruta de los archivos guardados
    """
    print("\nGenerando mapa de calor de distribución en Argentina...")
    
    # Cargar el archivo de shapefile de Argentina
    try:
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
        # Diccionario de mapeo para nombres que pueden diferir
        mapeo = {
            'Ciudad Autónoma de Buenos Aires': 'Buenos Aires',
            'CABA': 'Buenos Aires',
            'Tierra del Fuego': 'Tierra del Fuego, Antártida e Islas del Atlántico Sur',
            'Santiago Del Estero': 'Santiago del Estero'
        }
        
        # Aplicar mapeo si existe
        if nombre in mapeo:
            return mapeo[nombre]
        
        # Normalizar texto para comparaciones
        return nombre.lower().replace(' ', '').replace('á', 'a').replace('é', 'e').replace('í', 'i').replace('ó', 'o').replace('ú', 'u')
    
    # Aplicar normalización a ambos DataFrames
    argentina_map['provincia_norm'] = argentina_map['provincia_nombre'].apply(normalizar_nombre)
    rodriguez_provincias['provincia_norm'] = rodriguez_provincias['provincia_nombre'].apply(normalizar_nombre)
    
    if 'provincia_nombre' in joaquin_por_provincia.columns:
        joaquin_por_provincia['provincia_norm'] = joaquin_por_provincia['provincia_nombre'].apply(normalizar_nombre)
    
    # Unir datos
    merged_rodriguez = argentina_map.merge(rodriguez_provincias, on='provincia_norm', how='left')
    
    # Manejar valores nulos
    merged_rodriguez['cantidad'] = merged_rodriguez['cantidad'].fillna(0)
    
    # Preparar datos para Joaquín
    if 'provincia_nombre' in joaquin_por_provincia.columns:
        merged_joaquin = argentina_map.merge(joaquin_por_provincia, on='provincia_norm', how='left')
        merged_joaquin['cantidad_joaquin'] = merged_joaquin['cantidad_joaquin'].fillna(0)
    else:
        print("No se encontraron datos provinciales para el nombre Joaquín")
        merged_joaquin = merged_rodriguez.copy()
        merged_joaquin['cantidad_joaquin'] = 0
    
    # Calcular estimación de la combinación Joaquín Rodríguez por provincia
    # Basado en la distribución proporcional del estimado global
    merged_combinacion = merged_rodriguez.copy()
    
    # Si hay datos de ambos, calcular la combinación por provincia
    if 'cantidad' in merged_rodriguez.columns and 'cantidad_joaquin' in merged_joaquin.columns:
        total_rodriguez = merged_rodriguez['cantidad'].sum()
        
        if total_rodriguez > 0 and estimacion_global > 0:
            # Distribuir el estimado global proporcionalmente según la distribución de Rodriguez
            merged_combinacion['estimacion_joaquin_rodriguez'] = merged_rodriguez['cantidad'] / total_rodriguez * estimacion_global
        else:
            # Si no hay estimación global, hacer una aproximación basada en ambas distribuciones
            merged_combinacion['estimacion_joaquin_rodriguez'] = merged_rodriguez['cantidad'] * \
                                                      merged_joaquin['cantidad_joaquin'] / \
                                                      (merged_joaquin['cantidad_joaquin'].sum() or 1) * 0.01
    else:
        merged_combinacion['estimacion_joaquin_rodriguez'] = 0
    
    # Convertir a GeoJSON para Bokeh
    geo_source_rodriguez = GeoJSONDataSource(geojson=merged_rodriguez.to_json())
    geo_source_joaquin = GeoJSONDataSource(geojson=merged_joaquin.to_json())
    geo_source_combinacion = GeoJSONDataSource(geojson=merged_combinacion.to_json())
    
    # Definir paletas de colores para cada mapa (usar diferentes paletas para diferenciar)
    palette_rodriguez = Viridis256
    palette_joaquin = Turbo256
    palette_combinacion = RdYlBu11
    
    # Crear mapas de colores
    color_mapper_rodriguez = LinearColorMapper(palette=palette_rodriguez, 
                                              low=merged_rodriguez['cantidad'].min(),
                                              high=merged_rodriguez['cantidad'].max())
    
    color_mapper_joaquin = LinearColorMapper(palette=palette_joaquin, 
                                           low=merged_joaquin['cantidad_joaquin'].min(), 
                                           high=merged_joaquin['cantidad_joaquin'].max())
    
    color_mapper_combinacion = LinearColorMapper(palette=palette_combinacion, 
                                               low=merged_combinacion['estimacion_joaquin_rodriguez'].min(),
                                               high=merged_combinacion['estimacion_joaquin_rodriguez'].max())
    
    # Aumentar el tamaño de las figuras
    figure_width = 700
    figure_height = 600

    # Crear figuras con el nuevo tamaño
    p1 = figure(title="Distribución del apellido Rodríguez por provincia",
                height=figure_height, width=figure_width, toolbar_location="right")
    p1.patches('xs', 'ys', source=geo_source_rodriguez,
              fill_color={'field': 'cantidad', 'transform': color_mapper_rodriguez},
              line_color='black', line_width=0.5, fill_alpha=0.7)
    
    # Añadir barra de color
    color_bar_rodriguez = ColorBar(color_mapper=color_mapper_rodriguez, 
                                 label_standoff=12, border_line_color=None,
                                 location=(0, 0), title='Cantidad de personas')
    p1.add_layout(color_bar_rodriguez, 'right')
    
    # Añadir hover
    hover_rodriguez = HoverTool(tooltips=[
        ('Provincia', '@provincia_nombre_y'),
        ('Cantidad', '@cantidad{0,0}')
    ])
    p1.add_tools(hover_rodriguez)
    
    # Mapa para nombre Joaquín
    p2 = figure(title="Distribución del nombre Joaquín por provincia",
                height=figure_height, width=figure_width, toolbar_location="right")
    p2.patches('xs', 'ys', source=geo_source_joaquin,
             fill_color={'field': 'cantidad_joaquin', 'transform': color_mapper_joaquin},
             line_color='black', line_width=0.5, fill_alpha=0.7)
    
    # Añadir barra de color
    color_bar_joaquin = ColorBar(color_mapper=color_mapper_joaquin, 
                               label_standoff=12, border_line_color=None,
                               location=(0, 0), title='Cantidad de personas')
    p2.add_layout(color_bar_joaquin, 'right')
    
    # Añadir hover
    hover_joaquin = HoverTool(tooltips=[
        ('Provincia', '@provincia_nombre_y'),
        ('Cantidad', '@cantidad_joaquin{0,0}')
    ])
    p2.add_tools(hover_joaquin)
    
    # Mapa para la combinación Joaquín Rodríguez
    p3 = figure(title="Estimación de Joaquín Rodríguez por provincia",
                height=figure_height, width=figure_width, toolbar_location="right")
    p3.patches('xs', 'ys', source=geo_source_combinacion,
             fill_color={'field': 'estimacion_joaquin_rodriguez', 'transform': color_mapper_combinacion},
             line_color='black', line_width=0.5, fill_alpha=0.7)
    
    # Añadir barra de color
    color_bar_combinacion = ColorBar(color_mapper=color_mapper_combinacion, 
                                   label_standoff=12, border_line_color=None,
                                   location=(0, 0), title='Estimación')
    p3.add_layout(color_bar_combinacion, 'right')
    
    # Añadir hover
    hover_combinacion = HoverTool(tooltips=[
        ('Provincia', '@provincia_nombre_y'),
        ('Estimación', '@estimacion_joaquin_rodriguez{0,0}')
    ])
    p3.add_tools(hover_combinacion)
    
    # Quitar ejes
    for p in [p1, p2, p3]:
        p.axis.visible = False
        p.grid.grid_line_color = None
    
    # Guardar mapas individuales
    reset_output()  # Reiniciar el documento de salida
    output_file("visualizaciones/mapa_rodriguez_provincias.html")
    save(p1)
    print("Mapa de apellido Rodríguez guardado en visualizaciones/mapa_rodriguez_provincias.html")
    
    reset_output()  # Reiniciar el documento de salida
    output_file("visualizaciones/mapa_joaquin_provincias.html")
    save(p2)
    print("Mapa de nombre Joaquín guardado en visualizaciones/mapa_joaquin_provincias.html")
    
    reset_output()  # Reiniciar el documento de salida
    output_file("visualizaciones/mapa_joaquin_rodriguez_provincias.html")
    save(p3)
    print("Mapa de estimación Joaquín Rodríguez guardado en visualizaciones/mapa_joaquin_rodriguez_provincias.html")
    
    # Crear un layout combinado con los tres mapas
    reset_output()  # Reiniciar el documento de salida

    # Crear nuevas instancias de las figuras para evitar reutilización
    p1_layout = figure(title="Distribución del apellido Rodríguez por provincia",
                       height=500, width=500, toolbar_location="right")
    p1_layout.patches('xs', 'ys', source=GeoJSONDataSource(geojson=merged_rodriguez.to_json()),
                      fill_color={'field': 'cantidad', 'transform': LinearColorMapper(palette=Viridis256,
                                                                                     low=merged_rodriguez['cantidad'].min(),
                                                                                     high=merged_rodriguez['cantidad'].max())},
                      line_color='black', line_width=0.5, fill_alpha=0.7)

    p2_layout = figure(title="Distribución del nombre Joaquín por provincia",
                       height=500, width=500, toolbar_location="right")
    p2_layout.patches('xs', 'ys', source=GeoJSONDataSource(geojson=merged_joaquin.to_json()),
                      fill_color={'field': 'cantidad_joaquin', 'transform': LinearColorMapper(palette=Turbo256,
                                                                                             low=merged_joaquin['cantidad_joaquin'].min(),
                                                                                             high=merged_joaquin['cantidad_joaquin'].max())},
                      line_color='black', line_width=0.5, fill_alpha=0.7)

    p3_layout = figure(title="Estimación de Joaquín Rodríguez por provincia",
                       height=500, width=500, toolbar_location="right")
    p3_layout.patches('xs', 'ys', source=GeoJSONDataSource(geojson=merged_combinacion.to_json()),
                      fill_color={'field': 'estimacion_joaquin_rodriguez', 'transform': LinearColorMapper(palette=RdYlBu11,
                                                                                                         low=merged_combinacion['estimacion_joaquin_rodriguez'].min(),
                                                                                                         high=merged_combinacion['estimacion_joaquin_rodriguez'].max())},
                      line_color='black', line_width=0.5, fill_alpha=0.7)

    # Crear el layout con las nuevas figuras
    layout = row(p1_layout, p2_layout, p3_layout)
    output_file("visualizaciones/mapas_comparativos_argentina.html")
    save(layout)
    print("Mapa comparativo guardado en visualizaciones/mapas_comparativos_argentina.html")
    
    # Crear un filtro interactivo
    select = Select(title="Selecciona la distribución:", value="Rodríguez",
                    options=["Rodríguez", "Joaquín", "Joaquín Rodríguez"])

    # Crear nuevas instancias de las figuras para el layout interactivo
    p1_interactive = figure(title="Distribución del apellido Rodríguez por provincia",
                            height=figure_height, width=figure_width, toolbar_location="right")
    p1_interactive.patches('xs', 'ys', source=GeoJSONDataSource(geojson=merged_rodriguez.to_json()),
                           fill_color={'field': 'cantidad', 'transform': LinearColorMapper(palette=Viridis256,
                                                                                          low=merged_rodriguez['cantidad'].min(),
                                                                                          high=merged_rodriguez['cantidad'].max())},
                           line_color='black', line_width=0.5, fill_alpha=0.7)

    p2_interactive = figure(title="Distribución del nombre Joaquín por provincia",
                            height=figure_height, width=figure_width, toolbar_location="right")
    p2_interactive.patches('xs', 'ys', source=GeoJSONDataSource(geojson=merged_joaquin.to_json()),
                           fill_color={'field': 'cantidad_joaquin', 'transform': LinearColorMapper(palette=Turbo256,
                                                                                                low=merged_joaquin['cantidad_joaquin'].min(),
                                                                                                high=merged_joaquin['cantidad_joaquin'].max())},
                           line_color='black', line_width=0.5, fill_alpha=0.7)

    p3_interactive = figure(title="Estimación de Joaquín Rodríguez por provincia",
                            height=figure_height, width=figure_width, toolbar_location="right")
    p3_interactive.patches('xs', 'ys', source=GeoJSONDataSource(geojson=merged_combinacion.to_json()),
                           fill_color={'field': 'estimacion_joaquin_rodriguez', 'transform': LinearColorMapper(palette=RdYlBu11,
                                                                                                              low=merged_combinacion['estimacion_joaquin_rodriguez'].min(),
                                                                                                              high=merged_combinacion['estimacion_joaquin_rodriguez'].max())},
                           line_color='black', line_width=0.5, fill_alpha=0.7)

    # Crear un callback para alternar entre las distribuciones
    callback = CustomJS(args=dict(p1=p1_interactive, p2=p2_interactive, p3=p3_interactive, select=select), code="""
        p1.visible = false;
        p2.visible = false;
        p3.visible = false;

        if (select.value === "Rodríguez") {
            p1.visible = true;
        } else if (select.value === "Joaquín") {
            p2.visible = true;
        } else if (select.value === "Joaquín Rodríguez") {
            p3.visible = true;
        }
    """)
    select.js_on_change('value', callback)

    # Hacer visibles solo los gráficos iniciales
    p1_interactive.visible = True
    p2_interactive.visible = False
    p3_interactive.visible = False

    # Crear el layout interactivo
    layout_interactive = column(select, p1_interactive, p2_interactive, p3_interactive)

    # Guardar el layout interactivo
    reset_output()
    output_file("visualizaciones/mapas_interactivos_argentina.html")
    save(layout_interactive)
    print("Mapa interactivo guardado en visualizaciones/mapas_interactivos_argentina.html")

    # Calcular algunos insights para el informe
    max_rodriguez_provincia = merged_rodriguez.loc[merged_rodriguez['cantidad'].idxmax()]['provincia_nombre_y']
    max_joaquin_provincia = merged_joaquin.loc[merged_joaquin['cantidad_joaquin'].idxmax()]['provincia_nombre_y']
    max_combinacion_provincia = merged_combinacion.loc[merged_combinacion['estimacion_joaquin_rodriguez'].idxmax()]['provincia_nombre_y']
    
    return (f"Se generaron mapas de calor que muestran la distribución de personas con apellido Rodríguez, "
            f"nombre Joaquín y la combinación Joaquín Rodríguez. La mayor concentración de Rodríguez se encuentra en "
            f"{max_rodriguez_provincia}, la de Joaquín en {max_joaquin_provincia} y la combinación estimada en "
            f"{max_combinacion_provincia}.")