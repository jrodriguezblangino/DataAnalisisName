# test_mapa_argentina.py
import pandas as pd
import geopandas as gpd
import warnings
import numpy as np
warnings.filterwarnings('ignore')

# Importa la función del archivo que acabas de crear
from mapa_calor_argentina import generar_mapa_distribucion_argentina

# Verifica que no haya conflictos con otros módulos o nombres de archivo
# Asegúrate de que no exista un archivo llamado `mapa_calor_argentina.py` en otro directorio del proyecto
# que pueda estar causando conflictos en las importaciones.

# Cargar los mismos datasets que usas en tu proyecto principal
print("Cargando datos...")
apellidos_provincia = pd.read_csv('docs/apellidos_cantidad_personas_provincia_clean.csv')
historico_nombres = pd.read_csv('docs/historico-nombres_clean.csv')

# Preparar datos para Rodríguez
rodriguez_provincias = apellidos_provincia[apellidos_provincia['apellido'].str.lower() == 'rodriguez']
if len(rodriguez_provincias) == 0:
    rodriguez_provincias = apellidos_provincia[apellidos_provincia['apellido'].str.lower() == 'rodríguez']

rodriguez_provincias = rodriguez_provincias.groupby('provincia_nombre').agg({'cantidad': 'sum'}).reset_index()

# Preparar datos para Joaquín
joaquin_historico = historico_nombres[historico_nombres['nombre'].str.lower() == 'joaquin']
if len(joaquin_historico) == 0:
    joaquin_historico = historico_nombres[historico_nombres['nombre'].str.lower() == 'joaquín']

# Comprobar si tenemos provincia_nombre en joaquin_historico
if 'provincia_nombre' in joaquin_historico.columns:
    joaquin_por_provincia = joaquin_historico.groupby('provincia_nombre')['cantidad'].sum().reset_index()
    joaquin_por_provincia.rename(columns={'cantidad': 'cantidad_joaquin'}, inplace=True)
else:
    print("ADVERTENCIA: No hay datos de provincia para Joaquín. Creando dataset simulado.")
    provincias = rodriguez_provincias['provincia_nombre'].unique()
    cantidades = np.random.randint(10, 1000, size=len(provincias))
    joaquin_por_provincia = pd.DataFrame({
        'provincia_nombre': provincias,
        'cantidad_joaquin': cantidades
    })

# Mostrar un resumen de los datos
print(f"Datos de Rodríguez: {len(rodriguez_provincias)} provincias")
print(f"Datos de Joaquín: {len(joaquin_por_provincia)} provincias")

# Definir una estimación global de Joaquín Rodríguez
estimacion_global = 1000

# Probar la función
resultado = generar_mapa_distribucion_argentina(
    rodriguez_provincias, 
    joaquin_por_provincia, 
    estimacion_global
)

print("\nResultado:")
print(resultado)