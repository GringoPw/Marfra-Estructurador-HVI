import pandas as pd
from constants import COLUMNAS_ESTANDAR, grado_mapping
import re

#Funciones principales
def cargar_datos(ruta_archivo, longitud_sub_id):
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
            datos = cargar_datos_formato_tres(ruta_archivo, longitud_sub_id)
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


def procesar_sub_id(sub_id, longitud_sub_id):
    """
    Extrae los últimos `longitud_sub_id` dígitos del campo de Sub ID.
    Si no es numérico o más corto que la longitud deseada, lo devuelve como está.
    """
    
    
    try:
        
        sub_id_str = str(sub_id).strip().replace(" ", "")

        # Asegurar que sea completamente numérico
        if not sub_id_str.isdigit():
            return sub_id_str

        if len(sub_id_str) >= longitud_sub_id:
            return sub_id_str[-longitud_sub_id:]

        return sub_id_str  # Si es más corto, devolverlo igual

    except Exception as e:
        print(f"Error procesando Sub ID '{sub_id}': {e}")
        return str(sub_id)


def filtrar_datos_limpios(ruta_archivo, debug=False):
    """
    Elimina encabezados, estadísticas y líneas inválidas.
    Reconstruye líneas partidas y Sub ID divididos en dos columnas.
    """
    import re

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
        r"^\s*$",
        r"tifier.*MGTA.*LOTE"
    ]

    lineas_limpias = []
    buffer_linea = None

    try:
        with open(ruta_archivo, 'r', encoding='latin1') as archivo:
            lineas = archivo.readlines()

        for i, linea in enumerate(lineas):
            linea_limpia = linea.strip()
            if not linea_limpia:
                continue

            if any(re.search(p, linea_limpia, re.IGNORECASE) for p in patrones_sucios):
                if debug:
                    print(f"[Línea {i+1}] Eliminada por patrón: {linea_limpia}")
                continue

            partes = linea_limpia.split()
            # 🔧 Caso especial: Más de 16 columnas - fusionar las dos primeras
            if len(partes) > 16:
                partes[0] = partes[0] + partes[1]  # Fusionar las dos primeras columnas
                partes.pop(1)  # Eliminar la segunda columna ahora fusionada
                if debug:
                    print(f"[Línea {i+1}] 🔧 Fusionadas columnas 1 y 2 por exceso de columnas: {linea_limpia}")

            # 🔧 Sub ID partido tipo '00 049420'
            if len(partes) >= 2 and re.match(r'^\d{2}$', partes[0]) and re.match(r'^\d{6}$', partes[1]):
                partes[0] = partes[0] + partes[1]  # unir Sub ID
                partes.pop(1)
                linea_limpia = " ".join(partes)
                if debug:
                    print(f"[Línea {i+1}] 🔧 Sub ID corregido: {linea_limpia}")

            # Si es un Sub ID suelto
            if len(partes) == 1 and re.match(r'^\d{5,}$', partes[0]):
                if buffer_linea:
                    buffer_partes = buffer_linea.split()
                    buffer_partes[0] = partes[0]
                    nueva_linea = " ".join(buffer_partes)
                    columnas = nueva_linea.split()
                    if 5 <= len(columnas) <= 16:
                        try:
                            float(columnas[0])
                            lineas_limpias.append(nueva_linea)
                            if debug:
                                print(f"[Línea {i+1}] ✅ Reconstruida: {nueva_linea}")
                        except ValueError:
                            if debug:
                                print(f"[Línea {i+1}] ❌ Sub ID inválido tras reconstrucción: {nueva_linea}")
                    else:
                        if debug:
                            print(f"[Línea {i+1}] ❌ Cols inválidas tras unir: {nueva_linea}")
                    buffer_linea = None
                else:
                    if debug:
                        print(f"[Línea {i+1}] ⚠️ Sub ID suelto sin línea previa: {linea_limpia}")
                continue

            if re.match(r'^\d{5,}$', partes[0]) and 5 <= len(partes) <= 16:
                try:
                    float(partes[0])
                    lineas_limpias.append(" ".join(partes))
                    if debug:
                        print(f"[Línea {i+1}] ✅ Aceptada normal: {' '.join(partes)}")
                    buffer_linea = None
                except ValueError:
                    buffer_linea = linea_limpia
                    if debug:
                        print(f"[Línea {i+1}] ❌ Sub ID inválido: {linea_limpia}")
            else:
                if "-" in partes[0]:
                    buffer_linea = linea_limpia
                    if debug:
                        print(f"[Línea {i+1}] ⏳ Posible línea partida: {linea_limpia}")
                else:
                    buffer_linea = None
                    try:
                        float(partes[0])
                        lineas_limpias.append(" ".join(partes))
                        if debug:
                            print(f"[Línea {i+1}] ✅ Aceptada (espaciada pero válida): {linea_limpia}")
                    except ValueError:
                        if debug:
                            print(f"[Línea {i+1}] ❌ No válida y sin guion: {linea_limpia}")

    except Exception as e:
        print(f"Error al procesar el archivo: {e}")
        return []

    if debug:
        print(f"\n✅ Total líneas válidas: {len(lineas_limpias)}")
    return lineas_limpias

# Ejemplo de uso en la función principal:
def cargar_datos_formato_tres(ruta_archivo, longitud_sub_id):
    """
    Carga y ajusta datos del formato 3 usando limpieza previa línea por línea.
    """
    try:
        # Limpiar las líneas
        print("Cargando datos del formato 3...")
        lineas_limpias = filtrar_datos_limpios(ruta_archivo, debug=True)

        
        # Convertirlas a DataFrame
        from io import StringIO
        datos_txt = '\n'.join(lineas_limpias)
        df = pd.read_csv(StringIO(datos_txt), sep=r'\s+', header=None)

        # Crear DataFrame con formato deseado
        datos_formato_deseado = pd.DataFrame(columns=COLUMNAS_ESTANDAR)

        # Asignación de columnas con protección
        datos_formato_deseado["Sub ID"] = df[0].apply(lambda x: procesar_sub_id(x, longitud_sub_id))  # Fixed this line
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
