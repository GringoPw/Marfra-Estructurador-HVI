import pandas as pd
from constants import COLUMNAS_ESTANDAR, grado_mapping
import re

#Funciones principales
def cargar_datos(ruta_archivo):
    """
    Lee el archivo de texto, detecta el formato y reorganiza los datos.
    """
    try:
        # Verifica el formato leyendo las primeras líneas del archivo con codificación específica
        with open(ruta_archivo, "r", encoding='latin1') as archivo:
            lineas = archivo.readlines()
        
        # Buscar identificadores en las primeras 10 líneas
        contenido_inicio = ''.join(lineas[:10])
        
        # Selecciona el formato en función del contenido
        if "HFT" in contenido_inicio:
            datos = cargar_datos_formato_dos(ruta_archivo)
            print("Formato 2 hfi")
        elif "PREMIER ART V1.1.8b" in contenido_inicio:
            datos = cargar_datos_formato_uno(ruta_archivo)
            print("Formato 1 art")
        else:
            datos = cargar_datos_formato_tres(ruta_archivo)
            print("Formato 3 art R")
        
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

def filtrar_metrica_formato3(df):
    """
    Filtra las filas con métricas específicas para el formato 3.
    Corta la lectura cuando encuentra 'Statistics' en cualquier columna.
    """
    try:
        # Buscar la fila donde aparece 'Statistics' en cualquier columna
        indices_stats = []
        
        for idx, row in df.iterrows():
            for col in df.columns:
                valor = str(row[col]).strip().upper()
                # Buscar 'STATISTICS' de forma más flexible
                
                if 'STATISTICS' in valor or valor == 'STATISTICS' or valor == '/ Temp( C)' :
                    indices_stats.append(idx)
                    print(f"Encontrado 'Statistics' en fila {idx}, columna {col}: '{row[col]}'")
                    break
        
        # Si encontramos 'Statistics', cortamos el DataFrame hasta esa fila (sin incluirla)
        if indices_stats:
            primer_stats = min(indices_stats)
            df = df.loc[:primer_stats-1]
            print(f"Cortado en fila {primer_stats} por encontrar 'Statistics'. Filas restantes: {len(df)}")
        else:
            print("No se encontró 'Statistics' en el archivo")
        
        # Filtros adicionales si es necesario
        df = df.dropna(how='all')  # Eliminar filas completamente vacías
        
        return df
    
    except Exception as e:
        print(f"Error en filtrar_metrica_formato3: {e}")
        return df


def procesar_sub_id(sub_id):
    """
    Procesa el Sub ID según las reglas:
    - Si tiene 7 o más dígitos: devuelve los últimos 6
    - Si tiene 5 o más dígitos: devuelve los últimos 4
    - Si tiene menos de 5 dígitos: devuelve el valor original
    """
    try:
        # Convertir a string y limpiar espacios
        sub_id_str = str(sub_id).strip()
        
        # Verificar si es numérico
        if not sub_id_str.isdigit():
            return sub_id_str
        
        # Aplicar las reglas según la longitud
        longitud = len(sub_id_str)
        
        if longitud >= 7:
            return sub_id_str[-6:]  # Últimos 6 dígitos
        elif longitud >= 5:
            return sub_id_str[-4:]  # Últimos 4 dígitos
        else:
            return sub_id_str       # Valor original
    
    except Exception as e:
        print(f"Error procesando Sub ID '{sub_id}': {e}")
        return str(sub_id)

def filtrar_datos_limpios(ruta_archivo, debug=False):
    """
    Elimina completamente las filas que contengan patrones de encabezados o estadísticas.
    Solo devuelve las filas que son datos puros.
    """
    patrones_sucios = [
        r"System Test Report",
        r"PREMIER ART R",
        r"\d{2}-\d{2}-\d{4}\d{2}:\d{2}[AP]M",
        r"Test ID",
        r"Test Type",
        r"Test Date",
        r"Remarks",
        r"COOP\.AGR",
        r"UHML.*ML.*UI.*Str.*Elg.*Mic",
        r"Test.*Sub ID.*\(mm\)",
        r"No.*\)",
        r"Statistics",
        r"Avg\d*-?\d*",
        r"Median",
        r"SD",
        r"CV%",
        r"Min",
        r"Max",
        r"MARFRA SA",
        r"Temp\(.*C\)",
        r"^\s*$",  # Líneas vacías
        r"^\s*\d+\s*$",  # Líneas con solo números
        r"tifier.*MGTA.*LOTE"
    ]
    
    lineas_limpias = []
    
    try:
        with open(ruta_archivo, 'r', encoding='latin1') as archivo:
            lineas = archivo.readlines()
        
        for i, linea in enumerate(lineas):
            linea_limpia = linea.strip()
            if not linea_limpia:
                continue

            # Revisar patrones sucios
            if any(re.search(p, linea_limpia, re.IGNORECASE) for p in patrones_sucios):
                if debug:
                    print(f"Eliminada (patrón sucio): {linea_limpia}")
                continue

            partes = linea_limpia.split()

            # Filtrar por exceso de columnas
            if len(partes) > 16:
                if debug:
                    print(f"Eliminada (demasiadas columnas {len(partes)}): {linea_limpia}")
                continue

            # Validar si el primer campo es numérico
            try:
                float(partes[0])
                lineas_limpias.append(linea_limpia)
                if debug:
                    print(f"Aceptada: {linea_limpia}")
            except ValueError:
                if debug:
                    print(f"Eliminada (primer campo no numérico): {linea_limpia}")
                continue

    except Exception as e:
        print(f"Error al procesar el archivo: {e}")
        return []

    if debug:
        print(f"\nResumen: {len(lineas_limpias)} líneas válidas encontradas")

    return lineas_limpias

# Ejemplo de uso en la función principal:
def cargar_datos_formato_tres(ruta_archivo):
    """
    Carga y ajusta datos del formato 3 usando limpieza previa línea por línea.
    """
    try:
        # Limpiar las líneas
        print("Cargando datos del formato 3...")
        lineas_limpias = filtrar_datos_limpios(ruta_archivo)
        
        # Convertirlas a DataFrame
        from io import StringIO
        datos_txt = '\n'.join(lineas_limpias)
        df = pd.read_csv(StringIO(datos_txt), sep=r'\s+', header=None)

        # Crear DataFrame con formato deseado
        datos_formato_deseado = pd.DataFrame(columns=COLUMNAS_ESTANDAR)

        # Asignación de columnas con protección
        datos_formato_deseado["Sub ID"] = df[0].apply(procesar_sub_id)
        datos_formato_deseado["UHML"] = df[1]
        datos_formato_deseado["ML"] = df[2]
        datos_formato_deseado["UI"] = df[3]
        datos_formato_deseado["Str"] = df[4]
        datos_formato_deseado["Elg"] = df[5]
        datos_formato_deseado["Mic"] = df[6]
        datos_formato_deseado["Amt"] = df[7]
        datos_formato_deseado["Rd"] = df[8]
        datos_formato_deseado["+b"] = df[9]
        datos_formato_deseado["CG"] = df[10]

        # Grado y SAP
        datos_formato_deseado["Grado"] = df[10].apply(obtener_grado)
        datos_formato_deseado["Grado SAP"] = datos_formato_deseado["Grado"].map(grado_mapping)

        # Columnas opcionales
        datos_formato_deseado["T.Cnt"] = df[11] if df.shape[1] > 11 else ""
        datos_formato_deseado["T.Area"] = df[12] if df.shape[1] > 12 else ""
        datos_formato_deseado["Leaf"] = df[13] if df.shape[1] > 13 else ""
        datos_formato_deseado["MR"] = df[14] if df.shape[1] > 14 else ""
        datos_formato_deseado["SFI"] = df[15] if df.shape[1] > 15 else ""

        # Ordenar y validar
        datos_formato_deseado["Sub ID"] = pd.to_numeric(datos_formato_deseado["Sub ID"], errors="coerce")
        datos_formato_deseado.sort_values(by=["Sub ID"], inplace=True)
        validar_sub_id_consecutivos(datos_formato_deseado)
        return datos_formato_deseado

    except Exception as e:
        print(f"Error al cargar el archivo en formato 3: {e}")
        return pd.DataFrame()



    """
    Elimina completamente las filas que contengan patrones de encabezados o estadísticas.
    Solo devuelve las filas que son datos puros.
    
    Args:
        ruta_archivo (str): Ruta al archivo de texto
        debug (bool): Si True, imprime información de depuración
    
    Returns:
        list: Lista de líneas que contienen solo datos puros
    """
    
    # Patrones que indican líneas "sucias" a eliminar completamente
    patrones_sucios = [
        r"System Test Report",
        r"PREMIER ART R",
        r"\d{2}-\d{2}-\d{4}\d{2}:\d{2}[AP]M",
        r"Test ID",
        r"Test Type",
        r"Test Date",
        r"Remarks",
        r"COOP\.AGR",
        r"UHML.*ML.*UI.*Str.*Elg.*Mic",
        r"Test.*Sub ID.*\(mm\)",
        r"No.*\)",
        r"Statistics",
        r"Avg\d*-?\d*",
        r"Median",
        r"SD",
        r"CV%",
        r"Min",
        r"Max",
        r"MARFRA SA",
        r"Temp\(.*C\)",
        r"^\s*$",  # Líneas vacías
        r"^\s*\d+\s*$",  # Líneas con solo uno o dos números (páginas)
        r"tifier.*MGTA.*LOTE"  # Identificadores de lote
    ]
    
    lineas_limpias = []
    
    try:
        with open(ruta_archivo, 'r', encoding='latin1') as archivo:
            lineas = archivo.readlines()
        
        for i, linea in enumerate(lineas):
            linea_limpia = linea.strip()
            
            # Si la línea está vacía, saltarla
            if not linea_limpia:
                continue
            
            # Verificar si contiene algún patrón sucio
            es_sucia = False
            for patron in patrones_sucios:
                if re.search(patron, linea_limpia, re.IGNORECASE):
                    es_sucia = True
                    if debug:
                        print(f"Línea {i+1} eliminada por patrón '{patron}': {linea_limpia[:60]}...")
                    break
            
            # Si es sucia, eliminar completamente
            if es_sucia:
                continue
            
            # Verificar si parece ser una línea de datos válida
            partes = linea_limpia.split()
            if len(partes) >= 5:  # Mínimo de columnas esperadas
                try:
                    # El primer elemento debe ser numérico (Sub ID)
                    float(partes[0])
                    lineas_limpias.append(linea_limpia)
                    if debug:
                        print(f"Línea {i+1} aceptada: {linea_limpia[:60]}...")
                except ValueError:
                    if debug:
                        print(f"Línea {i+1} eliminada (primer campo no numérico): {linea_limpia[:60]}...")
                    continue
            else:
                if debug:
                    print(f"Línea {i+1} eliminada (pocas columnas): {linea_limpia[:60]}...")
    
    except Exception as e:
        print(f"Error al procesar el archivo: {e}")
        return []
    
    if debug:
        print(f"\nResumen: {len(lineas_limpias)} líneas de datos válidas encontradas")
    
    return lineas_limpias