import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import webbrowser
from constants import COLUMNAS_ESTANDAR
from data_processor import cargar_datos, validar_sub_id_consecutivos
from utils import copiar_al_portapapeles, promediar

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

    def marcar_errores(self, event=None):
        # Marcar errores al hacer clic en el indicador
        for idx in self.errores_indices:
            item = self.tree.get_children()[idx]
            self.tree.item(item, tags=("error",))
    
    def actualizar_info_label(self):
        # Actualizar texto de la etiqueta con filas y errores
        color = "#22c55e" if self.total_errores == 0 else "#ef4444"
        self.info_label.configure(
            text=f"Filas: {self.total_filas} | Errores: {self.total_errores}",
            fg=color
        )
    
    def procesar_datos(self, datos):
        # Limpiar datos existentes en el Treeview
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Validar errores usando la función proporcionada
        self.errores_indices = validar_sub_id_consecutivos(datos)

        # Insertar datos en el Treeview
        for i, row in datos.iterrows():
            tag = 'evenrow' if i % 2 == 0 else 'oddrow'
            if i in self.errores_indices:
                tag = 'error'
            valores = [i + 1] + row.tolist()
            self.tree.insert('', 'end', values=valores, tags=(tag,))
        
        # Actualizar contadores
        self.total_filas = len(datos)
        
        self.total_errores = len(self.errores_indices)
        print(f"Total filas: {self.total_filas}, Total errores: {self.total_errores}")

        self.actualizar_info_label()

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



