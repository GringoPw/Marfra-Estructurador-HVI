import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import webbrowser
from constants import COLUMNAS_ESTANDAR
from data_processor import cargar_datos, validar_sub_id_consecutivos
from utils import copiar_al_portapapeles, promediar
import os


class ModernInterface(tk.Tk):
    def __init__(self):
        super().__init__()
        
        # Configuración básica de la ventana
        self.title("Estructurador de datos - V3.4B")
        self.geometry("1200x700")
        self.configure(bg="#f0f4f8")
        
        # Variables de estado
        self.dark_mode = False
        self.errores_indices = []  # Índices de filas con errores
        self.total_filas = 0
        self.total_errores = 0
        
        # Crear estilos personalizados
        self.style = ttk.Style()
        self.style.theme_use('default')
        self.style.configure(
            "Custom.Treeview",
            background="white",
            foreground="black",
            rowheight=30,
            fieldbackground="white"
        )
        self.style.configure(
            "Custom.Treeview.Heading",
            background="#f8fafc",
            foreground="black",
            relief="flat",
            font=('Arial', 10, 'bold')
        )

        # Header Frame
        self.header_frame = tk.Frame(self, bg="#ffffff", pady=10, padx=15)
        self.header_frame.pack(fill="x", pady=(0, 10))
        self.subid_digitos = tk.IntVar(value=5)  # Valor por defecto, cámbialo si es necesario

        self.title_label = tk.Label(
            self.header_frame,
            text="Estructurador de Datos",
            font=("Arial", 14, "bold"),
            bg="#ffffff",
            fg="black"
        )
        self.title_label.pack(side="left")
        
        self.contact_btn = tk.Button(
            self.header_frame,
            text="Contactar",
            command=self.mostrar_contacto,
            bg="#ffffff",
            fg="#4b5563",
            relief="solid",
            bd=1,
            padx=15
        )
        self.contact_btn.pack(side="right")

        self.dark_mode_btn = tk.Button(
            self.header_frame,
            text="Modo Oscuro",
            command=self.toggle_dark_mode,
            bg="#ffffff",
            fg="#4b5563",
            relief="solid",
            bd=1,
            padx=15
        )
        self.dark_mode_btn.pack(side="right", padx=5)
        

        # Tabla Frame
        self.table_frame = tk.Frame(self, bg="white", pady=10)
        self.table_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Header de la tabla
        self.table_header = tk.Frame(self.table_frame, bg="white", pady=10, padx=10)
        self.table_header.pack(fill="x")
        
        
        
        self.info_label = tk.Label(
            self.table_header,
            text="Archivo: | Filas: 0 | Errores: 0",
            font=("Arial", 12),
            bg="#ffffff",
            fg="#6b7280"
        )
        self.info_label.pack(side="left", padx=10)
        self.info_label.bind("<Button-1>", self.marcar_errores)
        
        # Botones Frame
        self.buttons_frame = tk.Frame(self.table_header, bg="white")
        self.buttons_frame.pack(side="right")
        
        button_style = {
            'bg': '#ffffff',
            'fg': '#4b5563',
            'relief': 'solid',
            'bd': 1,
            'padx': 15,
            'pady': 5
        }
        
        tk.Label(
            self.buttons_frame,
            text="Dígitos Sub ID:",
            bg="#ffffff",
            fg="#4b5563",
            font=("Arial", 10)
        ).pack(side="left", padx=(15, 5))

        tk.Entry(
            self.buttons_frame,
            textvariable=self.subid_digitos,
            width=5
        ).pack(side="left", padx=(0, 10))
        
        tk.Button(
            self.buttons_frame,
            text="Buscar TXT",
            command=self.buscar_archivo,
            **button_style
        ).pack(side="left", padx=5)
        
        tk.Button(
            self.buttons_frame,
            text="Copiar",
            command=self.copiar_portapapeles,
            **button_style
        ).pack(side="left", padx=5)

        # Frame contenedor para la tabla y scrollbars
        self.tree_frame = tk.Frame(self.table_frame)
        self.tree_frame.pack(fill="both", expand=True, padx=10)
        
        columns = ("#", "Grado SAP",
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
        "SFI")
        self.tree = ttk.Treeview(
            self.tree_frame,
            columns=columns,
            show="headings",
            style="Custom.Treeview",
            selectmode="extended"
        )

        self.tree.heading("#", text="#", anchor="center")
        self.tree.column("#", width=100, anchor="center", stretch=False)
        
        for col in columns[1:]:
            self.tree.heading(col, text=col, anchor="w")
            self.tree.column(
                col,
                width=100,
                anchor="w",
                stretch=True
            )
        
        # Scrollbars
        y_scroll = ttk.Scrollbar(self.tree_frame, orient="vertical", command=self.tree.yview)
        x_scroll = ttk.Scrollbar(self.tree_frame, orient="horizontal", command=self.tree.xview)
        
        self.tree.configure(yscrollcommand=y_scroll.set, xscrollcommand=x_scroll.set)
        x_scroll.pack(side="bottom", fill="x")
        y_scroll.pack(side="right", fill="y")
        self.tree.pack(side="left", fill="both", expand=True)
        
        # Configurar colores alternados para las filas
        self.tree.tag_configure('oddrow', background='#f8f9fa')
        self.tree.tag_configure('evenrow', background='white')
        self.tree.tag_configure('error', background='#fecaca', foreground='#991b1b')
        
        # Crear el tooltip
        self.tooltip = tk.Label(self, 
                              text="", 
                              bg="#ffedd5", 
                              fg="#9a3412",
                              relief="solid",
                              borderwidth=1)
        
        self.tree.bind("<Motion>", self.on_motion)
        self.tree.bind("<Leave>", self.on_leave)

    def toggle_dark_mode(self):
        self.dark_mode = not self.dark_mode
        
        if self.dark_mode:
            self.configure(bg="#1f2937")
           
            self.style.configure("Custom.Treeview", background="#374151", foreground="#ffffff", fieldbackground="#1f2937")
            self.style.configure("Custom.Treeview.Heading", background="#4b5563", foreground="#ffffff")
            
            # Actualizar más widgets para el modo oscuro
            self.header_frame.configure(bg="#1f2937")
            self.title_label.configure(bg="#1f2937", fg="#60a5fa")
            self.contact_btn.configure(bg="#374151", fg="#ffffff")
            self.dark_mode_btn.configure(bg="#374151", fg="#ffffff")
            self.table_frame.configure(bg="#1f2937")
            self.table_header.configure(bg="#1f2937")
            self.info_label.configure(bg="#1f2937", fg="#ffffff")
            self.buttons_frame.configure(bg="#1f2937")
            
            self.table_header.configure(bg="#1f2937")

            # Actualizar filas del Treeview
            self.tree.tag_configure('oddrow', background='#374151')
            self.tree.tag_configure('evenrow', background='#1f2937')

        else:
            self.configure(bg="#f0f4f8")
          
            self.style.configure("Custom.Treeview", background="white", foreground="black", fieldbackground="white")
            self.style.configure("Custom.Treeview.Heading", background="#f8fafc", foreground="black")
            
            # Restaurar los widgets a sus colores claros originales
            self.header_frame.configure(bg="#ffffff")
            self.title_label.configure(bg="#ffffff", fg="black")
            self.contact_btn.configure(bg="#ffffff", fg="#4b5563")
            self.dark_mode_btn.configure(bg="#ffffff", fg="#4b5563")
            self.table_frame.configure(bg="white")
            self.table_header.configure(bg="white")
            self.info_label.configure(bg="#ffffff", fg="#6b7280")
            self.buttons_frame.configure(bg="white")
            

            # Restaurar filas del Treeview
            self.tree.tag_configure('oddrow', background='#f8f9fa')
            self.tree.tag_configure('evenrow', background='white')


    ########################    
    def procesar_archivo(self, ruta_archivo):
        datos = cargar_datos(ruta_archivo, self.subid_digitos.get())
        if datos is not None:
            # Limpiar datos existentes
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            # Obtener errores con sus descripciones
            errores_list = validar_sub_id_consecutivos(datos)
            
            # Convertir la lista de errores a diccionario
            self.errores_indices = {}
            for error in errores_list:
                if isinstance(error, tuple):  # Si el error tiene descripción
                    idx, descripcion = error
                    if idx > 0:  # Para marcar la fila anterior
                        self.errores_indices[idx - 1] = descripcion
                else:  # Si el error es solo un índice
                    if error > 0:
                        self.errores_indices[error - 1] = "Error desconocido"
            
            # Insertar datos con colores alternados
            for i, row in datos.iterrows():
                tag = 'evenrow' if i % 2 == 0 else 'oddrow'
                valores = [i + 1] + list(row.values)
                self.tree.insert('', 'end', values=valores, tags=(tag,))
            
            # Actualizar contadores
            self.total_filas = len(datos)
            self.total_errores = len(self.errores_indices)
            self.nombre = os.path.basename(ruta_archivo)
            
            # Actualizar etiqueta de información
            self.actualizar_info_label()
            
    
    ################################        
    def actualizar_info_label(self):
        color = "#22c55e" if self.total_errores == 0 else "#ef4444"
        texto =f"Archivo: ({self.nombre}) | Filas: {self.total_filas} | Errores: {self.total_errores}"
        if self.total_errores > 0:
            texto += " (Click para resaltar)"
        self.info_label.configure(text=texto, fg=color)
    
    def marcar_errores(self, event=None):
        """Marca las filas anteriores a las que tienen errores"""
        if not self.errores_indices:
            messagebox.showinfo("Información", "No hay errores para marcar.")
            return
        
        # Restaurar todas las filas a su estado original
        for i, item in enumerate(self.tree.get_children()):
            tag = 'evenrow' if i % 2 == 0 else 'oddrow'
            self.tree.item(item, tags=(tag,))
        
        # Marcar las filas con errores
        items = self.tree.get_children()
        for error_idx in self.errores_indices:
            try:
                if 0 <= error_idx < len(items):
                    item = items[error_idx]
                    self.tree.item(item, tags=('error',))
                    self.tree.see(item)
            except IndexError as e:
                print(f"Error al marcar fila {error_idx}: {e}")

    def on_motion(self, event):
        """Muestra el tooltip cuando el mouse está sobre una fila con error"""
        item = self.tree.identify_row(event.y)
        if item:
            idx = self.tree.get_children().index(item)
            if idx in self.errores_indices:
                # Obtener la posición del mouse
                x, y = event.x_root, event.y_root
                # Configurar y mostrar el tooltip
                self.tooltip.configure(text=f"Error: {self.errores_indices[idx]}")
                self.tooltip.place(x=x + 10, y=y + 10)
            else:
                self.tooltip.place_forget()

    def on_leave(self, event):
        """Oculta el tooltip cuando el mouse sale del Treeview"""
        self.tooltip.place_forget()
    
    def mostrar_datos(self, datos):
        # Limpiar datos existentes
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Insertar nuevos datos con colores alternados
        for i, row in datos.iterrows():
            tag = 'evenrow' if i % 2 == 0 else 'oddrow'
            # Convertir la fila a una lista y agregar el índice al principio
            valores = [i + 1] + list(row.values)
            self.tree.insert('', 'end', values=valores, tags=(tag,))
          
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

        # Asegúrate de actualizar la etiqueta
        self.actualizar_info_label()     
               
######################################################
   
    def buscar_archivo(self):
        archivo = filedialog.askopenfilename(
            filetypes=[("Archivos de texto", "*.txt"), ("Todos los archivos", "*.*")]
        )
        if archivo:
            self.procesar_archivo(archivo)

    def mostrar_contacto(self):
        contact_window = tk.Toplevel(self)
        contact_window.title("Contacto")
        contact_window.geometry("300x200")
        contact_window.configure(bg="white")
        
        tk.Label(
            contact_window,
            text="Información de Contacto",
            font=("Arial", 14, "bold"),
            bg="white"
        ).pack(pady=10)
        
        tk.Label(
            contact_window,
            text="Email: joaquin.paw@gmail.com",
            bg="white"
        ).pack(pady=5)
        
        whatsapp_label = tk.Label(
            contact_window,
            text="WhatsApp: Click aquí",
            fg="blue",
            cursor="hand2",
            bg="white"
        )
        whatsapp_label.pack(pady=5)
        whatsapp_label.bind(
            "<Button-1>",
            lambda e: webbrowser.open("https://wa.me/543735416373")
        )

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
    
    
if __name__ == "__main__":
    app = ModernInterface()
    app.mainloop()