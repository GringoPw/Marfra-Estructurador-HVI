import pandas as pd
from constants import COLUMNAS_ESTANDAR, grado_mapping
import re

#Funciones principales
def cargar_datos(ruta_archivo):
    """
    Lee el archivo de texto, detecta el formato y reorganiza los datos.
    """
    try:
        # Verifica el formato leyendo la primera línea del archivo con codificación específica
        with open(ruta_archivo, "r", encoding='latin1') as archivo:
            header_line = archivo.readline().strip()
        
        # Selecciona el formato en función del contenido de la primera línea
        if "HFT" in header_line:
            datos = cargar_datos_formato_dos(ruta_archivo)
        else:
            datos = cargar_datos_formato_uno(ruta_archivo)
        
        # Verifica si datos es un DataFrame antes de acceder a .head()
        if datos is None:
            print("Error: No se pudo cargar el archivo en un DataFrame.")
            return pd.DataFrame()  # Retorna un DataFrame vacío en caso de error
        else:
            """ print("Datos cargados:", datos.head()) """  # Muestra las primeras filas del DataFrame para verificación

        return datos

    except UnicodeDecodeError as e:
        print(f"Error de decodificación: {e}")
    except Exception as e:
        print(f"Error al cargar el archivo: {e}")
    
    # En caso de error, retorna un DataFrame vacío
    return pd.DataFrame()

def cargar_datos_formato_uno(ruta_archivo):
    """
    Carga y ajusta datos del primer formato de archivo, asignando la columna 'Grado' sin desplazar datos.
    """
    # Cargar el archivo sin incluir "Grado" en el encabezado
    columnas_sin_grado = [
        "Sub ID",
        "UHML",
        "ML",
        "UI",
        "Str",
        "Elg",
        "Mic",
        "Amt",
        "Rd",
        "+b",
        "CG",
        "T.Cnt",
        "T.Area",
        "Leaf",
        "MR",
        "SFI",
    ]
    df = pd.read_csv(ruta_archivo, sep=r'\s+', skiprows=7, names=columnas_sin_grado)


    # Filtrar y procesar métricas si es necesario
    df = filtrar_metrica(df)

    # Asignar la columna "Grado" basada en el valor de "CG" y agregarla al DataFrame
    df.insert(0, "Grado", df["CG"].apply(obtener_grado))

    
    # Agregar la columna "Grado SAP" antes de "Grado"
    df.insert(0, "Grado SAP", df["Grado"].map(grado_mapping))
    
    # Validación de 'Sub ID'
    datosOrdenados = df
    datosOrdenados["Sub ID"] = pd.to_numeric(datosOrdenados["Sub ID"], errors="coerce")
    datosOrdenados.sort_values(by=['Sub ID'], inplace=True,ascending=True)
        
    validar_sub_id_consecutivos(datosOrdenados)
    
            
    return datosOrdenados
    

def cargar_datos_formato_dos(ruta_archivo):
    """
    Carga y ajusta datos del segundo formato de archivo, asignando cada columna a un vector y exportando el resultado a Excel.
    """
    try:
        # Cargar el archivo completo, omitiendo las primeras 5 filas de encabezado
        df = pd.read_csv(ruta_archivo, sep=r'\s+', skiprows=7, header=None)

        df = filtrar_metrica(df)

        # Crear un DataFrame vacío con el formato deseado
        datos_formato_deseado = pd.DataFrame(columns=COLUMNAS_ESTANDAR)

        # Agregar la columna "Grado SAP" antes de "Grado"
       
        # Llenar el DataFrame con los datos del archivo, asignando cada columna correspondiente
        datos_formato_deseado["Grado"] = df[11].apply(obtener_grado)
        datos_formato_deseado["Grado SAP"] = datos_formato_deseado["Grado"].map(grado_mapping)

        datos_formato_deseado["Sub ID"] = df[1]  # Suponiendo que "Sub ID" es la segunda columna
        datos_formato_deseado["UHML"] = df[2]  # "UHML" es la tercera columna
        datos_formato_deseado["ML"] = df[3]  # "ML" es la cuarta columna
        datos_formato_deseado["UI"] = df[4]  # "UI" es la quinta columna
        datos_formato_deseado["Str"] = df[6]  # "Str" es la sexta columna
        datos_formato_deseado["Elg"] = df[7]  # "Elg" es la séptima columna
        datos_formato_deseado["Mic"] = df[5]  # "Mic" es la octava columna
        datos_formato_deseado["Amt"] = df[8]  # "Amt" es la novena columna
        datos_formato_deseado["Rd"] = df[9]  # "Rd" es la décima columna
        datos_formato_deseado["+b"] = df[10]  # "+b" es la undécima columna
        datos_formato_deseado["CG"] = df[11]

        # Las columnas vacías
        datos_formato_deseado["T.Cnt"] = ""  # Columna vacía T.Cnt
        datos_formato_deseado["T.Area"] = ""  # Columna vacía T.Area
        datos_formato_deseado["Leaf"] = ""  # Columna vacía Leaf
        datos_formato_deseado["MR"] = df[12]  # "MR" es la duodécima columna
        datos_formato_deseado["SFI"] = df[13]  # "SFI" es la decimotercera columna

        
        # Validación de 'Sub ID'
        datosOrdenados = datos_formato_deseado
        datosOrdenados["Sub ID"] = pd.to_numeric(datosOrdenados["Sub ID"], errors="coerce")
        datosOrdenados.sort_values(by=['Sub ID'], inplace=True,ascending=True)
        
        validar_sub_id_consecutivos(datosOrdenados)
        
        return datosOrdenados
            
    except Exception as e:
        print(f"Error al cargar el archivo: {e}")

def obtener_grado(valor_cg):
    try:
        # Convertimos el valor a cadena y eliminamos espacios en blanco
        valor_str = str(valor_cg).strip()

        # Si el valor es 'nan', 'na', o vacio, devolvemos None
        if valor_str.lower() in ["nan", "na", ""]:
            return None

        # Verificar si hay un guion y extraer la parte antes del guion
        if "-" in valor_str:
            valor = int(
                valor_str.split("-")[0][:2]
            )  # Toma solo los primeros dos números antes del guion
        else:
            valor = int(
                valor_str[:2]
            )  # Si no hay guion, tomar los primeros dos números directamente

        # Imprimir el valor procesado para diagnóstico
        """ print(f"Consultando valor: {valor_str} -> Extraído: {valor}") """

        # Diccionario de traducción de grados
        traduccion_grados = {
            (11,30): "B 1/2",
            (31, 38): "C",
            (39, 39): "C 1/4",
            (40, 40): "C 1/2",
            (41, 49): "C 3/4",
            (50, 50): "D",
            (51, 59): "D 1/4",
            (60, 60): "D 1/2",
            (61, 69): "D 3/4",
            (70, 70): "E",
            (71, 79): "E 1/4",
            (80, 81): "F",
        }

        # Iteramos sobre el diccionario para encontrar el rango correspondiente
        for rango, grado in traduccion_grados.items():
            if rango[0] <= valor <= rango[1]:
                """ print(f"Valor {valor} se asigna a grado: {grado}") """
                return grado

        # Si no hay coincidencia, devolvemos None
        """ print(f"Valor {valor} no tiene un grado asignado.") """
        return None
    except Exception as e:
        print(f"Error al procesar el valor {valor_cg}: {e}")
        return None

def filtrar_metrica(datos):
    """
    Filtra las filas con métricas (Min, Max, Avg, etc.).
    """
    datos = datos[
        ~datos.iloc[:, 0].isin(["Min:", "Max:", "Avg:", "S.D:", "CV%:", "LS:", "No."])
    ]
    datos = datos[
        ~datos.iloc[:, 0].isin(["Avg:", "Min:", "Max:", "SD:", "CV%:", "Tests", "Test"])
    ]

    """
    Filtra las filas irrelevantes o basura del DataFrame, manteniendo solo filas con datos válidos.
    """

    
    
    datos = datos.dropna(how="all")  # Eliminar filas con todos los valores NaN

    patrones_no_deseados = [
    r"None", r"LS:", r"No\.", r"-{2,}", r"Test", r":",
    r"Reading\(s\)", r"Color"
]

    # Crear una expresión regular combinada
    regex_patrones = "|".join(patrones_no_deseados)

    # Eliminar filas con patrones indeseados
    datos = datos[~datos.apply(lambda row: row.astype(str).str.contains(regex_patrones, regex=True).any(), axis=1)]

    return datos

def validar_sub_id_consecutivos(df):
    """
    Valida la columna 'Sub ID' para:
    - Filas con valores no numéricos.
    - Filas con valores duplicados.
    - Filas con valores no consecutivos.
    - Filas con diferencia mayor a 1000 entre valores consecutivos.
    """
    errores = []
    try:
        # Convertir "Sub ID" a numérico, forzando errores a NaN
        df["Sub ID"] = pd.to_numeric(df["Sub ID"], errors="coerce")
        
        # Detectar filas con valores no numéricos (NaN)
        nan_indices = df.index[df["Sub ID"].isnull()].tolist()
        for idx in nan_indices:
            errores.append((idx, "Valor no numérico"))
        
        # Detectar filas con valores duplicados
        duplicados = df[df["Sub ID"].duplicated()].index.tolist()
        for idx in duplicados:
            errores.append((idx, "Duplicado"))
        
        # Verificar consecutividad y diferencias mayores a 1000
        for i in range(1, len(df)):
            # Filas no consecutivas
            if df["Sub ID"].iloc[i] != df["Sub ID"].iloc[i - 1] + 1:
                errores.append((i, "No correlativo"))
            
            # Diferencia mayor a 1000
            if abs(df["Sub ID"].iloc[i] - df["Sub ID"].iloc[i - 1]) > 1000:
                errores.append((i, "Falta un número"))

        # Eliminar duplicados en la lista de errores manteniendo la descripción
        errores = list(dict.fromkeys(errores))  # Elimina duplicados preservando el orden

    except Exception as e:
        print(f"Error en la validación de 'Sub ID': {e}")
    
    return errores