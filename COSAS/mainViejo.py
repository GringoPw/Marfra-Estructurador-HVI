import pandas as pd
import pyperclip

#Interf<z
import tkinter as tk
import webbrowser
from tkinter import messagebox, filedialog
from tkinter import ttk


COLUMNAS_ESTANDAR = [
    "Grado SAP",
    "Grado",
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

grado_mapping = {
    'B': 5, 'B 1/8': 5.5, 'B 1/4': 6, 'B 3/8': 6.5, 'B 1/2': 7, 'B 5/8': 7.5,
    'B 3/4': 8, 'B 7/8': 8.5, 'C': 9, 'C 1/8': 9.5, 'C 1/4': 10, 'C 3/8': 10.5,
    'C 1/2': 11, 'C 5/8': 11.5, 'C 3/4': 12, 'C 7/8': 12.5, 'D': 13, 'D 1/8': 13.5,
    'D 1/4': 14, 'D 3/8': 14.5, 'D 1/2': 15, 'D 5/8': 15.5, 'D 3/4': 16, 'D 7/8': 16.5,
    'E': 17, 'E 1/8': 17.5, 'E 1/4': 18, 'E 3/8': 18.5, 'E 1/2': 19, 'E 5/8': 19.5,
    'E 3/4': 20, 'E 7/8': 20.5, 'F': 21
}

#Interface
class InterfaceApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Estructurador de Datos")
        self.geometry("1000x600")  # Tamaño más grande para la tabla
        self.resizable(False, False)  # Evita cambiar el tamaño

        # Crear la barra de herramientas (frame superior)
        barra_superior = tk.Frame(self, bg="lightgray", height=10)
        barra_superior.pack(fill="x", side="top")

        # Crear un botón en la barra superior
        btn_contactar = tk.Button(
            barra_superior, text="Contactar", command=self.mostrar_contacto
        )
        btn_contactar.pack(side="right", padx=10)

        # Cambiar el color de fondo de la ventana
        self.configure(bg="#f0f0f0")  # Color de fondo claro

        # Título estilizado
        self.title_label = tk.Label(
            self,
            text="Estructurador de Datos",
            font=("Arial", 24, "bold"),
            bg="#4A90E2",
            fg="white",
            padx=10,
            pady=10,
        )
        self.title_label.pack(fill="x")  # Ocupa todo el ancho de la ventana

        # Etiqueta para arrastrar y soltar
        self.drop_label = tk.Label(
            self,
            text="Buscar el archivo.",
            font=("Arial", 18),
            width=30,
            height=6,
        )
        self.drop_label.pack(pady=10)

        

        # Crear un frame para el Treeview y las barras de desplazamiento
        frame = tk.Frame(self)
        frame.pack(expand=True, fill="both", padx=10, pady=10)

        # Crear el Treeview para mostrar la tabla
        self.tree = ttk.Treeview(frame, columns=(COLUMNAS_ESTANDAR), show="headings")

        # Configurar encabezados de la tabla
        for column in self.tree["columns"]:
            self.tree.heading(column, text=column)
            self.tree.column(column, anchor="center", width=100)  # Ajusta el ancho aquí

        # Crear barras de desplazamiento
        self.yscroll = ttk.Scrollbar(frame, orient="vertical", command=self.tree.yview)
        self.yscroll.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=self.yscroll.set)

        self.xscroll = ttk.Scrollbar(
            frame, orient="horizontal", command=self.tree.xview
        )
        self.xscroll.pack(side="bottom", fill="x")
        self.tree.configure(xscrollcommand=self.xscroll.set)

        self.tree.pack(expand=True, fill="both")

        # Botones en la parte inferior
        button_frame = tk.Frame(self)
        button_frame.pack(side=tk.BOTTOM, pady=10)

        self.search_button = tk.Button(
            button_frame, text="BUSCAR TXT", command=self.buscar_archivo
        )
        self.search_button.grid(row=0, column=0, padx=5)

        self.copy_button = tk.Button(
            button_frame,
            text="COPIAR AL PORTAPAPELES",
            command=self.copiar_portapapeles,
        )
        self.copy_button.grid(row=0, column=1, padx=5)

        self.export_button = tk.Button(
            button_frame, text="PROMEDIAR VALORES", command=self.promediar_val
        )
        self.export_button.grid(row=0, column=3, padx=5)

        # Botón "Contactar"
        """ self.contact_button = tk.Button(button_frame, text="CONTACTAR", command=self.mostrar_contacto)
        self.contact_button.grid(row=0, column=4, padx=5) """

    def on_drop(self, event):
        # Eliminar llaves de la ruta del archivo
        ruta_archivo = event.data.strip("{}")
        self.procesar_archivo(ruta_archivo)

    def buscar_archivo(self):
        ruta_archivo = filedialog.askopenfilename(
            title="Seleccionar archivo de texto",
            filetypes=(("Archivos de texto", "*.txt"), ("Todos los archivos", "*.*")),
        )
        if ruta_archivo:
            self.procesar_archivo(ruta_archivo)

    def procesar_archivo(self, ruta_archivo):
        # Cargar y procesar el archivo
        datos = cargar_datos(ruta_archivo)
        if datos is not None:
            self.mostrar_datos(datos)  # Mostrar datos en el Treeview

    def mostrar_datos(self, datos):
        # Limpiar el Treeview antes de mostrar nuevos datos
        for row in self.tree.get_children():
            self.tree.delete(row)

        # Insertar datos en el Treeview
        for index, row in datos.iterrows():
            self.tree.insert("", "end", values=list(row))

    def copiar_portapapeles(self):
        # Lógica para copiar datos al portapapeles
        if not self.tree.get_children():
            messagebox.showwarning(
                "Advertencia", "No hay datos para copiar al portapapeles."
            )
            return

        # Obtener los datos del Treeview
        datos = []
        for row in self.tree.get_children():
            datos.append(self.tree.item(row)["values"])

        # Llamar a la función de copiar del módulo main
        copiar_al_portapapeles(datos)  # Copiar datos al portapapeles
        self.tree.delete(*self.tree.get_children())  # Limpiar el Treeview

    def promediar_val(self):
        if not self.tree.get_children():
            messagebox.showwarning("Advertencia", "No hay datos para promediar.")
            return

        # Extraer los datos actuales del treeview
        datos = []
        for row in self.tree.get_children():
            datos.append(self.tree.item(row)["values"])

        # Pasar los datos a la función promediar
        promediar(datos, self.tree)

        # Actualizar los datos en el treeview
        for i, row in enumerate(self.tree.get_children()):
            self.tree.item(
                row, values=datos[i]
            )  # Actualizamos cada fila con los nuevos valores

        messagebox.showinfo(
            "Promediar", "Los valores se promediaron y actualizaron en el treeview."
        )

    def mostrar_contacto(self):
        # Crear una ventana personalizada para mostrar el contacto
        contacto_window = tk.Toplevel(self)
        contacto_window.title("Información de Contacto")
        contacto_window.geometry("300x200")
        contacto_window.configure(
            bg="#e3f2fd"
        )  # Color de fondo de la ventana de contacto

        # Etiqueta para el mensaje de contacto
        contacto_label = tk.Label(
            contacto_window, text="Contacto:", bg="#e3f2fd", font=("Arial", 12)
        )
        contacto_label.pack(pady=5)

        # Etiqueta para el correo
        correo_label = tk.Label(
            contacto_window,
            text="Correo: joaquin.paw@gmail.com",
            bg="#e3f2fd",
            font=("Arial", 12),
        )
        correo_label.pack(pady=5)

        # Crear un enlace clickeable para WhatsApp
        whatsapp_label = tk.Label(
            contacto_window,
            text="WhatsApp: https://wa.me/543735416373",
            bg="#e3f2fd",
            font=("Arial", 12),
            fg="blue",
            cursor="hand2",
        )
        whatsapp_label.pack(pady=5)
        whatsapp_label.bind(
            "<Button-1>", lambda e: webbrowser.open("https://wa.me/543735416373")
        )

        # Botón para cerrar la ventana
        close_button = tk.Button(
            contacto_window,
            text="Cerrar",
            command=contacto_window.destroy,
            bg="#4A90E2",
            fg="white",
        )
        close_button.pack(pady=10)

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
    
    return df

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

        
        """ print(f"{datos_formato_deseado}") """

        return datos_formato_deseado

    except Exception as e:
        print(f"Error al cargar el archivo: {e}")

# Función de traducción para obtener el grado
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

    patrones_no_deseados = [
    "None", "LS:", "No.", "----------------", "Test", ":",
    "Reading(s)", "Color"
    ]
    
    datos = datos.dropna(how="all")  # Eliminar filas con todos los valores NaN

    # Revisa cada fila y elimina aquellas que contengan patrones no deseados en cualquier columna
    datos = datos[~datos.apply(lambda row: row.astype(str).str.contains('|'.join(patrones_no_deseados)).any(), axis=1)]
    
    return datos

def verificar_correlatividad(sub_id_columna):
    """
    Verifica si los valores de 'sub_id' son correlativos.
    :param sub_id_columna: Columna 'sub_id' del DataFrame.
    :return: True si son correlativos, False si falta algún número.
    """
    # Verificar la secuencia de los 'sub_id'
    min_sub_id = sub_id_columna.min()
    max_sub_id = sub_id_columna.max()
    expected_rows = max_sub_id - min_sub_id + 1
    
    # Imprimir el mínimo, máximo y la cantidad de filas
    print(f"Min Sub ID: {min_sub_id}")
    print(f"Max Sub ID: {max_sub_id}")
    print(f"Cantidad de filas esperadas: {expected_rows}")
    print(f"Cantidad de filas reales: {len(sub_id_columna)}")

    # Verificar si la cantidad de filas es igual a las filas esperadas
    if len(sub_id_columna) != expected_rows:
        return False, min_sub_id, max_sub_id, expected_rows, len(sub_id_columna)
    
    # Verificar que todos los números entre min_sub_id y max_sub_id estén presentes
    missing_sub_ids = set(range(min_sub_id, max_sub_id + 1)) - set(sub_id_columna)
    if missing_sub_ids:
        return False, min_sub_id, max_sub_id, expected_rows, len(sub_id_columna)
    
    return True, min_sub_id, max_sub_id, expected_rows, len(sub_id_columna)

def copiar_al_portapapeles(datos):
    """
    Copia los datos a portapapeles para que se puedan pegar en Excel.
    Verifica que la columna 'sub_id' sea correlativa.
    
    :param datos: Lista de listas o DataFrame con los datos a copiar.
    """
    # Verificar si los datos son un DataFrame
    if isinstance(datos, pd.DataFrame):
        if 'Sub ID' in datos.columns:
            # En lugar de 'SubID', usa 'Sub ID'
            correlativo_valido, min_sub_id, max_sub_id, expected_rows, actual_rows = verificar_correlatividad(datos['Sub ID'])

            
            if not correlativo_valido:
                # Mostrar advertencia de error en la consola
                print(f"\033[91m¡Error! La columna 'sub_id' no es correlativa.\033[0m")
                print(f"\033[91mMin: {min_sub_id}, Max: {max_sub_id}, Filas esperadas: {expected_rows}, Filas reales: {actual_rows}\033[0m")
                return  # Salir sin copiar al portapapeles
            else:
                print(f"\033[92mVerificación exitosa: 'sub_id' es correlativa.\033[0m")
        else:
            # Advertencia si 'sub_id' no está en los datos
            print("\033[91m¡Error! La columna 'sub_id' no está presente en los datos.\033[0m")
            return  # Salir sin copiar al portapapeles
    
    # Convertir datos a un formato de texto adecuado
    if isinstance(datos, pd.DataFrame):
        datos_str = datos.to_csv(sep="\t", index=False, header=False)  # Usar tabulaciones para Excel
    else:
        datos_str = "\n".join(["\t".join(map(str, row)) for row in datos])  # Convertir lista a string

    # Copiar al portapapeles
    pyperclip.copy(datos_str)
    print("\033[92mDatos copiados al portapapaples.\033[0m")
   
def promediar(datos, treeview):
    # Inicializamos las sumas y el conteo para el promedio
    suma_uhml = suma_ui = suma_str = suma_mic = suma_sfi = 0
    conteo = len(datos)

    # Sumar los valores de las columnas UHML, UI, STR y MIC
    for fila in datos:
        try:
            suma_uhml += float(fila[3])  # Columna 2 para UHML
            suma_ui += float(fila[5])  # Columna 3 para UI
            suma_str += float(fila[6])  # Columna 4 para STR
            suma_mic += float(fila[8])  # Columna 5 para MIC
            suma_sfi += float(fila[17])  # Columna 15 para SFI
        except ValueError:
            print(f"Advertencia: los datos no son numéricos en la fila {fila}")
            continue  # Omite esta fila y sigue con las demás

    # Calcular los promedios y redondearlos a 1 decimal
    if conteo > 0:
        promedio_uhml = round(suma_uhml / conteo, 1)
        promedio_ui = round(suma_ui / conteo, 1)
        promedio_str = round(suma_str / conteo, 1)
        promedio_mic = round(suma_mic / conteo, 1)
        promedio_sfi = round(suma_sfi / conteo, 1)
    else:
        promedio_uhml = promedio_ui = promedio_str = promedio_mic = promedio_sfi = (
            0  # Valor predeterminado en caso de no haber datos
        )

    # Umbral de diferencia aceptable
    umbral = 4

    # Actualizar los valores en el dataframe y resaltar en rojo si fueron modificados
    for i in range(conteo):
        fila = datos[i]

        # Verificar si los valores están fuera del umbral y modificarlos
        if abs(float(fila[3]) - promedio_uhml) > umbral:  # Columna 2 para UHML
            fila[3] = promedio_uhml
            treeview.item(
                treeview.get_children()[i], values=fila
            )
            # Marcar solo la celda modificada
            treeview.tag_configure("modificado_uhml", background="red")
            treeview.item(
                treeview.get_children()[i], tags=("modificado_uhml",)
            )

        if abs(float(fila[5]) - promedio_ui) > umbral:  # Columna 4 para UI
            fila[5] = promedio_ui
            treeview.item(
                treeview.get_children()[i], values=fila
            )
            # Marcar solo la celda modificada
            treeview.tag_configure("modificado_ui", background="orange")
            treeview.item(
                treeview.get_children()[i], tags=("modificado_ui",)
            )

        if abs(float(fila[6]) - promedio_str) > umbral:  # Columna 5 para STR
            fila[6] = promedio_str
            treeview.item(
                treeview.get_children()[i], values=fila
            )
            # Marcar solo la celda modificada
            treeview.tag_configure("modificado_str", background="yellow")
            treeview.item(
                treeview.get_children()[i], tags=("modificado_str",)
            )

        if abs(float(fila[8]) - promedio_mic) > umbral:  # Columna 6 para MIC
            fila[8] = promedio_mic
            treeview.item(
                treeview.get_children()[i], values=fila
            )
            # Marcar solo la celda modificada
            treeview.tag_configure("modificado_mic", background="green")
            treeview.item(
                treeview.get_children()[i], tags=("modificado_mic",)
            )

        if abs(float(fila[17]) - promedio_sfi) > umbral:  # Columna 16 para MIC
            fila[17] = promedio_sfi
            treeview.item(
                treeview.get_children()[i], values=fila
            )
            # Marcar solo la celda modificada
            treeview.tag_configure("modificado_sfi", background="lightblue")
            treeview.item(
                treeview.get_children()[i], tags=("modificado_sfi",)
            )

    

if __name__ == "__main__":
    app = InterfaceApp()  # Inicia la interfaz
    app.mainloop()  # Mantén la ventana abierta
