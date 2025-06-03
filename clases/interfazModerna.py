import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import webbrowser
from constants import COLUMNAS_ESTANDAR
from data_processor import cargar_datos, validar_sub_id_consecutivos
from utils import copiar_al_portapapeles
import os
import pandas as pd
from errores import mostrar_error_lectura_archivo, mostrar_error_validacion, mostrar_error_procesamiento, mostrar_error_red, mostrar_error_general



class ModernInterface(tk.Tk):
    def __init__(self):
        super().__init__()
        
        # Configuración básica de la ventana
        self.title("Estructurador de Datos Profesional - V4.0")
        self.geometry("1400x800")
        self.state('zoomed')  # Maximizar ventana en Windows
        self.configure(bg="#f8fafc")
        
        # Variables de estado
        self.dark_mode = False
        self.errores_indices = {}
        self.total_filas = 0
        self.total_errores = 0
        self.datos_originales = None
        self.datos_filtrados = None
        self.editing_item = None
        self.editing_column = None
        
        # Variables de filtro y búsqueda
        self.search_var = tk.StringVar()
        self.filter_column = tk.StringVar()
        self.subid_digitos = tk.IntVar(value=5)
        
        # Crear estilos personalizados
        self.setup_styles()
        
        # Crear la interfaz
        self.create_header()
        self.create_toolbar()
        self.create_main_content()
        self.create_status_bar()
        
        # Configurar eventos
        self.setup_events()

    def setup_styles(self):
        """Configurar estilos personalizados para la interfaz"""
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Estilo para el Treeview principal
        self.style.configure(
            "Professional.Treeview",
            background="#ffffff",
            foreground="#1f2937",
            rowheight=32,
            fieldbackground="#ffffff",
            borderwidth=0,
            relief="flat"
        )
        
        self.style.configure(
            "Professional.Treeview.Heading",
            background="#e5e7eb",
            foreground="#374151",
            relief="flat",
            font=('Segoe UI', 10, 'bold'),
            borderwidth=1
        )
        
        # Estilo para botones
        self.style.configure(
            "Professional.TButton",
            padding=(12, 8),
            font=('Segoe UI', 9),
            relief="flat"
        )
        
        # Estilo para el frame principal
        self.style.configure(
            "Card.TFrame",
            background="#ffffff",
            relief="flat",
            borderwidth=1
        )

    def create_header(self):
        """Crear el header principal"""
        self.header_frame = tk.Frame(self, bg="#ffffff", height=80, relief="flat", bd=1)
        self.header_frame.pack(fill="x", pady=(0, 1))
        self.header_frame.pack_propagate(False)
        
        # Contenedor principal del header
        header_content = tk.Frame(self.header_frame, bg="#ffffff")
        header_content.pack(fill="both", expand=True, padx=20, pady=15)
        
        # Lado izquierdo - Título y subtitle
        left_frame = tk.Frame(header_content, bg="#ffffff")
        left_frame.pack(side="left", fill="y")
        
        title_label = tk.Label(
            left_frame,
            text="Estructurador de Datos",
            font=("Segoe UI", 18, "bold"),
            bg="#ffffff",
            fg="#1f2937"
        )
        title_label.pack(anchor="w")
        
        subtitle_label = tk.Label(
            left_frame,
            text="Análisis y edición profesional de datos",
            font=("Segoe UI", 10),
            bg="#ffffff",
            fg="#6b7280"
        )
        subtitle_label.pack(anchor="w")
        
        # Lado derecho - Botones de acción
        right_frame = tk.Frame(header_content, bg="#ffffff")
        right_frame.pack(side="right", fill="y")
        
        button_style = {
            'font': ('Segoe UI', 9),
            'relief': 'flat',
            'bd': 0,
            'padx': 16,
            'pady': 8,
            'cursor': 'hand2'
        }
        
        self.contact_btn = tk.Button(
            right_frame,
            text="📧 Contacto",
            command=self.mostrar_contacto,
            bg="#f3f4f6",
            fg="#374151",
            **button_style
        )
        self.contact_btn.pack(side="right", padx=(10, 0))
        
        self.dark_mode_btn = tk.Button(
            right_frame,
            text="🌙 Modo Oscuro",
            command=self.toggle_dark_mode,
            bg="#f3f4f6",
            fg="#374151",
            **button_style
        )
        self.dark_mode_btn.pack(side="right", padx=(10, 0))

    def create_toolbar(self):
        """Crear la barra de herramientas"""
        self.toolbar_frame = tk.Frame(self, bg="#f8fafc", height=60, relief="flat")
        self.toolbar_frame.pack(fill="x", pady=(0, 1))
        self.toolbar_frame.pack_propagate(False)
        
        toolbar_content = tk.Frame(self.toolbar_frame, bg="#f8fafc")
        toolbar_content.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Lado izquierdo - Controles de archivo
        left_toolbar = tk.Frame(toolbar_content, bg="#f8fafc")
        left_toolbar.pack(side="left", fill="y")
        
        button_style = {
            'font': ('Segoe UI', 9),
            'relief': 'flat',
            'bd': 0,
            'padx': 12,
            'pady': 6,
            'cursor': 'hand2'
        }
        
        tk.Button(
            left_toolbar,
            text="📁 Abrir Archivo",
            command=self.buscar_archivo,
            bg="#3b82f6",
            fg="white",
            **button_style
        ).pack(side="left", padx=(0, 10))
        
        tk.Button(
            left_toolbar,
            text="💾 Guardar",
            command=self.guardar_archivo,
            bg="#10b981",
            fg="white",
            **button_style
        ).pack(side="left", padx=(0, 10))
        
        tk.Button(
            left_toolbar,
            text="📋 Copiar",
            command=self.copiar_portapapeles,
            bg="#8b5cf6",
            fg="white",
            **button_style
        ).pack(side="left", padx=(0, 10))
        
        # Centro - Configuración de Sub ID
        center_toolbar = tk.Frame(toolbar_content, bg="#f8fafc")
        center_toolbar.pack(side="left", fill="y", padx=(30, 0))
        
        tk.Label(
            center_toolbar,
            text="Dígitos Sub ID:",
            bg="#f8fafc",
            fg="#374151",
            font=("Segoe UI", 9)
        ).pack(side="left", padx=(0, 5))
        
        subid_entry = tk.Entry(
            center_toolbar,
            textvariable=self.subid_digitos,
            width=5,
            font=("Segoe UI", 9),
            relief="flat",
            bd=1
        )
        subid_entry.pack(side="left", padx=(0, 10))
        
        # Lado derecho - Búsqueda y filtros
        right_toolbar = tk.Frame(toolbar_content, bg="#f8fafc")
        right_toolbar.pack(side="right", fill="y")
        
        tk.Label(
            right_toolbar,
            text="🔍 Buscar:",
            bg="#f8fafc",
            fg="#374151",
            font=("Segoe UI", 9)
        ).pack(side="left", padx=(0, 5))
        
        search_entry = tk.Entry(
            right_toolbar,
            textvariable=self.search_var,
            width=20,
            font=("Segoe UI", 9),
            relief="flat",
            bd=1
        )
        search_entry.pack(side="left", padx=(0, 10))
        
        tk.Button(
            right_toolbar,
            text="🔍",
            command=self.buscar_datos,
            bg="#6b7280",
            fg="white",
            font=("Segoe UI", 8),
            relief="flat",
            bd=0,
            padx=8,
            pady=6,
            cursor="hand2"
        ).pack(side="left", padx=(0, 10))
        
        tk.Button(
            right_toolbar,
            text="❌ Limpiar",
            command=self.limpiar_filtros,
            bg="#ef4444",
            fg="white",
            font=("Segoe UI", 8),
            relief="flat",
            bd=0,
            padx=8,
            pady=6,
            cursor="hand2"
        ).pack(side="left")

    def create_main_content(self):
        """Crear el contenido principal"""
        self.main_frame = tk.Frame(self, bg="#f8fafc")
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Panel de información
        self.info_panel = tk.Frame(self.main_frame, bg="#ffffff", height=50, relief="flat", bd=1)
        self.info_panel.pack(fill="x", pady=(0, 10))
        self.info_panel.pack_propagate(False)
        
        info_content = tk.Frame(self.info_panel, bg="#ffffff")
        info_content.pack(fill="both", expand=True, padx=20, pady=10)
        
        self.info_label = tk.Label(
            info_content,
            text="Archivo: No seleccionado | Filas: 0 | Errores: 0",
            font=("Segoe UI", 11, "bold"),
            bg="#ffffff",
            fg="#6b7280",
            cursor="hand2"
        )
        self.info_label.pack(side="left")
        self.info_label.bind("<Button-1>", self.marcar_errores)
        
        # Botones de acción adicionales
        action_frame = tk.Frame(info_content, bg="#ffffff")
        action_frame.pack(side="right")
        
        small_button_style = {
            'font': ('Segoe UI', 8),
            'relief': 'flat',
            'bd': 0,
            'padx': 8,
            'pady': 4,
            'cursor': 'hand2'
        }
        
        
        tk.Button(
            action_frame,
            text="🔄 Actualizar",
            command=self.actualizar_datos,
            bg="#06b6d4",
            fg="white",
            **small_button_style
        ).pack(side="left", padx=(0, 5))
        
        # Contenedor de la tabla
        self.table_container = tk.Frame(self.main_frame, bg="#ffffff", relief="flat", bd=1)
        self.table_container.pack(fill="both", expand=True)
        
        # Frame para la tabla y scrollbars
        self.tree_frame = tk.Frame(self.table_container, bg="#ffffff")
        self.tree_frame.pack(fill="both", expand=True, padx=1, pady=1)
        
        # Configurar el Treeview con todas las columnas
        columns = ("#", "Grado SAP", "Grado", "Sub ID", "UHML", "ML", "UI", "Str", 
                  "Elg", "Mic", "Amt", "Rd", "+b", "CG", "T.Cnt", "T.Area", "Leaf", "MR", "SFI")
        
        self.tree = ttk.Treeview(
            self.tree_frame,
            columns=columns,
            show="headings",
            style="Professional.Treeview",
            selectmode="extended"
        )
        
        # Configurar columnas
        self.tree.heading("#", text="#", anchor="center")
        self.tree.column("#", width=60, anchor="center", stretch=False)
        
        for col in columns[1:]:
            self.tree.heading(col, text=col, anchor="center")
            self.tree.column(col, width=100, anchor="center", stretch=True)
        
        # Scrollbars mejoradas
        y_scrollbar = ttk.Scrollbar(self.tree_frame, orient="vertical", command=self.tree.yview)
        x_scrollbar = ttk.Scrollbar(self.tree_frame, orient="horizontal", command=self.tree.xview)
        
        self.tree.configure(yscrollcommand=y_scrollbar.set, xscrollcommand=x_scrollbar.set)
        
        # Posicionar scrollbars y treeview
        x_scrollbar.pack(side="bottom", fill="x")
        y_scrollbar.pack(side="right", fill="y")
        self.tree.pack(side="left", fill="both", expand=True)
        
        # Configurar tags para colores
        self.tree.tag_configure('oddrow', background='#f9fafb')
        self.tree.tag_configure('evenrow', background='#ffffff')
        self.tree.tag_configure('error', background='#fef2f2', foreground='#dc2626')
        self.tree.tag_configure('selected', background='#dbeafe', foreground='#1e40af')

    def create_status_bar(self):
        """Crear la barra de estado"""
        self.status_frame = tk.Frame(self, bg="#e5e7eb", height=30, relief="flat")
        self.status_frame.pack(fill="x", side="bottom")
        self.status_frame.pack_propagate(False)
        
        self.status_label = tk.Label(
            self.status_frame,
            text="Listo",
            font=("Segoe UI", 9),
            bg="#e5e7eb",
            fg="#374151"
        )
        self.status_label.pack(side="left", padx=20, pady=5)
        
        # Información adicional en el lado derecho
        self.version_label = tk.Label(
            self.status_frame,
            text="v4.0 Professional",
            font=("Segoe UI", 8),
            bg="#e5e7eb",
            fg="#6b7280"
        )
        self.version_label.pack(side="right", padx=20, pady=5)

    def setup_events(self):
        """Configurar eventos y bindings"""
        # Eventos de edición
        self.tree.bind("<Double-1>", self.on_double_click)
        self.tree.bind("<Return>", self.on_enter_key)
        self.tree.bind("<Button-3>", self.show_context_menu)
        
        # Eventos de búsqueda
        self.search_var.trace('w', self.on_search_change)
        
        # Eventos de teclado
        self.bind("<Control-o>", lambda e: self.buscar_archivo())
        self.bind("<Control-s>", lambda e: self.guardar_archivo())
        self.bind("<Control-c>", lambda e: self.copiar_portapapeles())
        self.bind("<F5>", lambda e: self.actualizar_datos())

    def on_double_click(self, event):
        """Manejar doble clic para edición"""
        item = self.tree.selection()[0] if self.tree.selection() else None
        if not item:
            return
        
        column = self.tree.identify_column(event.x)
        if column == '#1':  # No editar la columna de índice
            return
        
        self.start_edit(item, column)

    def start_edit(self, item, column):
        """Iniciar edición de celda"""
        if self.editing_item:
            self.finish_edit()
        
        self.editing_item = item
        self.editing_column = column
        
        # Obtener posición y tamaño de la celda
        bbox = self.tree.bbox(item, column)
        if not bbox:
            return
        
        x, y, width, height = bbox
        
        # Crear entry para edición
        self.edit_entry = tk.Entry(self.tree)
        self.edit_entry.place(x=x, y=y, width=width, height=height)
        
        # Obtener valor actual
        col_index = int(column[1:]) - 1
        current_value = self.tree.item(item)['values'][col_index]
        
        self.edit_entry.insert(0, str(current_value))
        self.edit_entry.select_range(0, tk.END)
        self.edit_entry.focus()
        
        # Eventos para finalizar edición
        self.edit_entry.bind('<Return>', lambda e: self.finish_edit(True))
        self.edit_entry.bind('<Escape>', lambda e: self.finish_edit(False))
        self.edit_entry.bind('<FocusOut>', lambda e: self.finish_edit(True))

    def finish_edit(self, save=True):
        """Finalizar edición de celda"""
        if not self.editing_item or not hasattr(self, 'edit_entry'):
            return
        
        if save:
            new_value = self.edit_entry.get()
            col_index = int(self.editing_column[1:]) - 1
            
            # Actualizar valor en el treeview
            values = list(self.tree.item(self.editing_item)['values'])
            values[col_index] = new_value
            self.tree.item(self.editing_item, values=values)
            
            # Actualizar datos originales si existen
            if self.datos_originales is not None:
                row_index = int(values[0]) - 1  # El primer valor es el índice
                if 0 <= row_index < len(self.datos_originales):
                    col_name = self.datos_originales.columns[col_index - 1]  # -1 porque excluimos el índice
                    self.datos_originales.iloc[row_index, col_index - 1] = new_value
        
        self.edit_entry.destroy()
        self.editing_item = None
        self.editing_column = None

    def show_context_menu(self, event):
        """Mostrar menú contextual"""
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            
            context_menu = tk.Menu(self, tearoff=0)
            context_menu.add_command(label="✏️ Editar", command=lambda: self.start_edit(item, '#2'))
            context_menu.add_separator()
            context_menu.add_command(label="📋 Copiar fila", command=self.copiar_fila)
            context_menu.add_command(label="🗑️ Eliminar fila", command=self.eliminar_fila)
            context_menu.add_separator()
            context_menu.add_command(label="🔍 Buscar similar", command=self.buscar_similar)
            
            try:
                context_menu.tk_popup(event.x_root, event.y_root)
            finally:
                context_menu.grab_release()

    def buscar_datos(self):
        """Buscar datos en la tabla"""
        if not self.datos_originales is not None:
            return
        
        search_term = self.search_var.get().lower()
        if not search_term:
            self.mostrar_datos(self.datos_originales)
            return
        
        # Filtrar datos
        mask = self.datos_originales.astype(str).apply(
            lambda x: x.str.lower().str.contains(search_term, na=False)
        ).any(axis=1)
        
        datos_filtrados = self.datos_originales[mask]
        self.mostrar_datos(datos_filtrados)
        
        self.update_status(f"Encontradas {len(datos_filtrados)} filas")

    def limpiar_filtros(self):
        """Limpiar filtros y búsqueda"""
        self.search_var.set("")
        if self.datos_originales is not None:
            self.mostrar_datos(self.datos_originales)
        self.update_status("Filtros limpiados")

    def on_search_change(self, *args):
        """Manejar cambios en el campo de búsqueda"""
        # Implementar búsqueda en tiempo real con un pequeño delay
        if hasattr(self, 'search_timer'):
            self.after_cancel(self.search_timer)
        self.search_timer = self.after(300, self.buscar_datos)

    def toggle_dark_mode(self):
        """Alternar modo oscuro"""
        self.dark_mode = not self.dark_mode
        
        if self.dark_mode:
            # Aplicar tema oscuro
            bg_dark = "#1f2937"
            fg_light = "#f9fafb"
            accent = "#3b82f6"
            
            self.configure(bg=bg_dark)
            self.header_frame.configure(bg="#111827")
            self.toolbar_frame.configure(bg="#374151")
            self.main_frame.configure(bg=bg_dark)
            
            # Actualizar estilos del treeview
            self.style.configure("Professional.Treeview", 
                               background="#374151", 
                               foreground=fg_light, 
                               fieldbackground="#1f2937")
            self.style.configure("Professional.Treeview.Heading", 
                               background="#4b5563", 
                               foreground=fg_light)
            
            self.dark_mode_btn.configure(text="☀️ Modo Claro")
            
        else:
            # Aplicar tema claro
            self.configure(bg="#f8fafc")
            self.header_frame.configure(bg="#ffffff")
            self.toolbar_frame.configure(bg="#f8fafc")
            self.main_frame.configure(bg="#f8fafc")
            
            # Restaurar estilos del treeview
            self.style.configure("Professional.Treeview", 
                               background="#ffffff", 
                               foreground="#1f2937", 
                               fieldbackground="#ffffff")
            self.style.configure("Professional.Treeview.Heading", 
                               background="#e5e7eb", 
                               foreground="#374151")
            
            self.dark_mode_btn.configure(text="🌙 Modo Oscuro")

    def procesar_archivo(self, ruta_archivo):
        """Versión mejorada del procesamiento con manejo de errores"""
        try:
            self.update_status("Cargando archivo...")
            datos = cargar_datos(ruta_archivo, self.subid_digitos.get())

            if datos is not None:
                self.datos_originales = datos.copy()
                self.mostrar_datos(datos)

                # Validar errores
                errores_list = validar_sub_id_consecutivos(datos)

                # Procesar errores para el diálogo
                error_types = {}
                error_list = []

                for error in errores_list:
                    if isinstance(error, tuple):
                        idx, descripcion = error
                        error_list.append({
                            'line': idx,
                            'message': descripcion
                        })

                        # Categorizar error
                        if "consecutivo" in descripcion.lower():
                            error_types["Sub ID no consecutivo"] = error_types.get("Sub ID no consecutivo", 0) + 1
                        else:
                            error_types["Error de formato"] = error_types.get("Error de formato", 0) + 1
                    else:
                        error_list.append({
                            'line': error,
                            'message': "Error desconocido"
                        })

                self.error_list = error_list  # ✅ Asignación correcta

                if error_list:
                    # Mostrar diálogo de errores
                    result = mostrar_error_validacion(
                        self,
                        len(error_list),
                        error_types,
                        error_list
                    )

                    # Procesar resultado si es necesario
                    if result == "retry":
                        return self.procesar_archivo_con_errores(ruta_archivo)

                self.total_filas = len(datos)
                self.total_errores = len(error_list)
                self.nombre_archivo = os.path.basename(ruta_archivo)

                self.actualizar_info_label()
                self.update_status(f"Archivo cargado: {self.nombre_archivo}")

        except FileNotFoundError:
            mostrar_error_lectura_archivo(
                self,
                ruta_archivo,
                "El archivo especificado no fue encontrado."
            )
        except PermissionError:
            mostrar_error_lectura_archivo(
                self,
                ruta_archivo,
                "No tiene permisos para leer este archivo."
            )
        except Exception as e:
            mostrar_error_general(
                self,
                "Error Inesperado",
                f"Ha ocurrido un error inesperado: {str(e)}"
            )
        
    
    def mostrar_datos(self, datos):
        """Mostrar datos en la tabla"""
        # Limpiar datos existentes
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Insertar datos con colores alternados
        for i, (idx, row) in enumerate(datos.iterrows()):
            tag = 'evenrow' if i % 2 == 0 else 'oddrow'
            valores = [i + 1] + list(row.values)
            self.tree.insert('', 'end', values=valores, tags=(tag,))

    def actualizar_info_label(self):
        """Actualizar etiqueta de información"""
        color = "#10b981" if self.total_errores == 0 else "#ef4444"
        texto = f"Archivo: {self.nombre_archivo} | Filas: {self.total_filas} | Errores: {self.total_errores}"
        if self.total_errores > 0:
            texto += " (Click para resaltar)"
        self.info_label.configure(text=texto, fg=color)

    def marcar_errores(self, event=None):
        """Marcar filas con errores"""
        if not hasattr(self, 'error_list') or not self.error_list:
            messagebox.showinfo("Información", "No hay errores para marcar.")
            return

        # Restaurar colores originales
        for i, item in enumerate(self.tree.get_children()):
            tag = 'evenrow' if i % 2 == 0 else 'oddrow'
            self.tree.item(item, tags=(tag,))

        # Marcar errores
        items = list(self.tree.get_children())
        for error in self.error_list:
            idx = error['line'] - 1  # Convertir a índice base 0
            if 0 <= idx < len(items):
                item = items[idx]
                self.tree.item(item, tags=('error',))
                self.tree.see(item)

    def buscar_archivo(self):
        """Buscar y abrir archivo"""
        archivo = filedialog.askopenfilename(
            title="Seleccionar archivo de datos",
            filetypes=[
                ("Archivos de texto", "*.txt"),
                ("Archivos CSV", "*.csv"),
                ("Todos los archivos", "*.*")
            ]
        )
        if archivo:
            self.procesar_archivo(archivo)

    def guardar_archivo(self):
        """Guardar datos actuales"""
        if self.datos_originales is None:
            messagebox.showwarning("Advertencia", "No hay datos para guardar.")
            return
        
        archivo = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[
                ("Archivos CSV", "*.csv"),
                ("Archivos de texto", "*.txt"),
                ("Todos los archivos", "*.*")
            ]
        )
        
        if archivo:
            try:
                self.datos_originales.to_csv(archivo, index=False, sep=";")  # Separador cambiado a ";"
                messagebox.showinfo("Éxito", f"Archivo guardado: {os.path.basename(archivo)}")
                self.update_status(f"Archivo guardado: {os.path.basename(archivo)}")
            except Exception as e:
                messagebox.showerror("Error", f"Error al guardar: {str(e)}")

    def copiar_portapapeles(self):
        """Copiar datos al portapapeles"""
        if not self.tree.get_children():
            messagebox.showwarning("Advertencia", "No hay datos para copiar.")
            return
        
        try:
            datos = []
            for row in self.tree.get_children():
                datos.append(self.tree.item(row)["values"])
            
            copiar_al_portapapeles(datos)
            messagebox.showinfo("Éxito", "Datos copiados al portapapeles")
            self.update_status("Datos copiados al portapapeles")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al copiar: {str(e)}")

    def actualizar_datos(self):
        """Actualizar datos y validaciones"""
        if self.datos_originales is not None:
            self.procesar_archivo(getattr(self, 'ruta_archivo_actual', ''))
            self.update_status("Datos actualizados")

    def copiar_fila(self):
        """Copiar fila seleccionada"""
        selection = self.tree.selection()
        if selection:
            values = self.tree.item(selection[0])['values']
            # Implementar lógica de copiado
            self.update_status("Fila copiada")

    def eliminar_fila(self):
        """Eliminar fila seleccionada"""
        selection = self.tree.selection()
        if not selection:
            return
        
        if messagebox.askyesno("Confirmar", "¿Está seguro de eliminar la fila seleccionada?"):
            item = selection[0]
            row_index = int(self.tree.item(item)['values'][0]) - 1
            
            # Eliminar del DataFrame original
            if self.datos_originales is not None and 0 <= row_index < len(self.datos_originales):
                self.datos_originales = self.datos_originales.drop(self.datos_originales.index[row_index]).reset_index(drop=True)
                self.mostrar_datos(self.datos_originales)
                self.update_status("Fila eliminada")

    def buscar_similar(self):
        """Buscar filas similares a la seleccionada"""
        selection = self.tree.selection()
        if not selection:
            return
        
        values = self.tree.item(selection[0])['values']
        sub_id = values[3] if len(values) > 3 else ""  # Columna Sub ID
        
        if sub_id:
            self.search_var.set(str(sub_id))
            self.buscar_datos()

    def mostrar_contacto(self):
        """Mostrar ventana de contacto mejorada"""
        contact_window = tk.Toplevel(self)
        contact_window.title("Información de Contacto")
        contact_window.geometry("400x300")
        contact_window.configure(bg="#ffffff")
        contact_window.resizable(False, False)
        contact_window.transient(self)
        contact_window.grab_set()
        
        # Centrar ventana
        contact_window.update_idletasks()
        x = (contact_window.winfo_screenwidth() // 2) - (400 // 2)
        y = (contact_window.winfo_screenheight() // 2) - (300 // 2)
        contact_window.geometry(f"400x300+{x}+{y}")
        
        # Header
        header_frame = tk.Frame(contact_window, bg="#3b82f6", height=60)
        header_frame.pack(fill="x")
        header_frame.pack_propagate(False)
        
        tk.Label(
            header_frame,
            text="📧 Información de Contacto",
            font=("Segoe UI", 16, "bold"),
            bg="#3b82f6",
            fg="white"
        ).pack(expand=True)
        
        # Content
        content_frame = tk.Frame(contact_window, bg="#ffffff")
        content_frame.pack(fill="both", expand=True, padx=30, pady=30)
        
        # Email
        email_frame = tk.Frame(content_frame, bg="#ffffff")
        email_frame.pack(fill="x", pady=(0, 20))
        
        tk.Label(
            email_frame,
            text="📧 Email:",
            font=("Segoe UI", 12, "bold"),
            bg="#ffffff",
            fg="#374151"
        ).pack(anchor="w")
        
        email_label = tk.Label(
            email_frame,
            text="joaquin.paw@gmail.com",
            font=("Segoe UI", 11),
            fg="#3b82f6",
            cursor="hand2",
            bg="#ffffff"
        )
        email_label.pack(anchor="w", pady=(5, 0))
        email_label.bind("<Button-1>", lambda e: webbrowser.open("mailto:joaquin.paw@gmail.com"))
        
        # WhatsApp
        whatsapp_frame = tk.Frame(content_frame, bg="#ffffff")
        whatsapp_frame.pack(fill="x", pady=(0, 20))
        
        tk.Label(
            whatsapp_frame,
            text="📱 WhatsApp:",
            font=("Segoe UI", 12, "bold"),
            bg="#ffffff",
            fg="#374151"
        ).pack(anchor="w")
        
        whatsapp_label = tk.Label(
            whatsapp_frame,
            text="+54 3735 416373",
            font=("Segoe UI", 11),
            fg="#10b981",
            cursor="hand2",
            bg="#ffffff"
        )
        whatsapp_label.pack(anchor="w", pady=(5, 0))
        whatsapp_label.bind("<Button-1>", lambda e: webbrowser.open("https://wa.me/543735416373"))
        
        # Versión
        tk.Label(
            content_frame,
            text="Estructurador de Datos v4.0 Professional",
            font=("Segoe UI", 9),
            bg="#ffffff",
            fg="#6b7280"
        ).pack(side="bottom", pady=(20, 0))
        
        # Botón cerrar
        tk.Button(
            content_frame,
            text="Cerrar",
            command=contact_window.destroy,
            bg="#6b7280",
            fg="white",
            font=("Segoe UI", 10),
            relief="flat",
            bd=0,
            padx=20,
            pady=8,
            cursor="hand2"
        ).pack(side="bottom", pady=(10, 0))

    def update_status(self, message):
        """Actualizar barra de estado"""
        self.status_label.configure(text=message)
        self.after(3000, lambda: self.status_label.configure(text="Listo"))

    def on_enter_key(self, event):
        """Manejar tecla Enter"""
        selection = self.tree.selection()
        if selection:
            self.start_edit(selection[0], '#2')

    def exportar_datos(self):
        """Exportar datos a diferentes formatos"""
        if self.datos_originales is None:
            messagebox.showwarning("Advertencia", "No hay datos para exportar.")
            return
        
        export_window = tk.Toplevel(self)
        export_window.title("Exportar Datos")
        export_window.geometry("300x200")
        export_window.configure(bg="#ffffff")
        export_window.transient(self)
        export_window.grab_set()
        
        tk.Label(
            export_window,
            text="Seleccione el formato de exportación:",
            font=("Segoe UI", 12),
            bg="#ffffff"
        ).pack(pady=20)
        
        formats = [
            ("CSV (Comma Separated)", "csv"),
            ("Excel (.xlsx)", "xlsx"),
            ("JSON", "json"),
            ("Texto plano", "txt")
        ]
        
        for text, fmt in formats:
            tk.Button(
                export_window,
                text=text,
                command=lambda f=fmt: self.export_format(f, export_window),
                bg="#3b82f6",
                fg="white",
                font=("Segoe UI", 10),
                relief="flat",
                bd=0,
                padx=20,
                pady=8,
                cursor="hand2"
            ).pack(pady=5, padx=20, fill="x")

    def export_format(self, format_type, window):
        """Exportar en el formato especificado"""
        extensions = {
            'csv': '.csv',
            'xlsx': '.xlsx', 
            'json': '.json',
            'txt': '.txt'
        }
        
        filetypes = {
            'csv': [("CSV files", "*.csv")],
            'xlsx': [("Excel files", "*.xlsx")],
            'json': [("JSON files", "*.json")],
            'txt': [("Text files", "*.txt")]
        }
        
        archivo = filedialog.asksaveasfilename(
            defaultextension=extensions[format_type],
            filetypes=filetypes[format_type] + [("All files", "*.*")]
        )
        
        if archivo:
            try:
                if format_type == 'csv':
                    self.datos_originales.to_csv(archivo, index=False)
                elif format_type == 'xlsx':
                    self.datos_originales.to_excel(archivo, index=False)
                elif format_type == 'json':
                    self.datos_originales.to_json(archivo, orient='records', indent=2)
                elif format_type == 'txt':
                    self.datos_originales.to_csv(archivo, sep='\t', index=False)
                
                messagebox.showinfo("Éxito", f"Datos exportados a {os.path.basename(archivo)}")
                self.update_status(f"Exportado: {os.path.basename(archivo)}")
                window.destroy()
                
            except Exception as e:
                messagebox.showerror("Error", f"Error al exportar: {str(e)}")

    def importar_datos(self):
        """Importar datos desde diferentes formatos"""
        import_window = tk.Toplevel(self)
        import_window.title("Importar Datos")
        import_window.geometry("300x200")
        import_window.configure(bg="#ffffff")
        import_window.transient(self)
        import_window.grab_set()
        
        tk.Label(
            import_window,
            text="Seleccione el tipo de archivo:",
            font=("Segoe UI", 12),
            bg="#ffffff"
        ).pack(pady=20)
        
        formats = [
            ("Archivo de texto (.txt)", "txt"),
            ("CSV (.csv)", "csv"),
            ("Excel (.xlsx)", "xlsx")
        ]
        
        for text, fmt in formats:
            tk.Button(
                import_window,
                text=text,
                command=lambda f=fmt: self.import_format(f, import_window),
                bg="#10b981",
                fg="white",
                font=("Segoe UI", 10),
                relief="flat",
                bd=0,
                padx=20,
                pady=8,
                cursor="hand2"
            ).pack(pady=5, padx=20, fill="x")

    def import_format(self, format_type, window):
        """Importar desde el formato especificado"""
        filetypes = {
            'txt': [("Text files", "*.txt")],
            'csv': [("CSV files", "*.csv")],
            'xlsx': [("Excel files", "*.xlsx")]
        }
        
        archivo = filedialog.askopenfilename(
            filetypes=filetypes[format_type] + [("All files", "*.*")]
        )
        
        if archivo:
            window.destroy()
            if format_type == 'txt':
                self.procesar_archivo(archivo)
            else:
                try:
                    if format_type == 'csv':
                        datos = pd.read_csv(archivo)
                    elif format_type == 'xlsx':
                        datos = pd.read_excel(archivo)
                    
                    self.datos_originales = datos
                    self.mostrar_datos(datos)
                    self.total_filas = len(datos)
                    self.total_errores = 0
                    self.nombre_archivo = os.path.basename(archivo)
                    self.actualizar_info_label()
                    self.update_status(f"Importado: {self.nombre_archivo}")
                    
                except Exception as e:
                    messagebox.showerror("Error", f"Error al importar: {str(e)}")

    def mostrar_estadisticas(self):
        """Mostrar estadísticas de los datos"""
        if self.datos_originales is None:
            messagebox.showwarning("Advertencia", "No hay datos cargados.")
            return
        
        stats_window = tk.Toplevel(self)
        stats_window.title("Estadísticas de Datos")
        stats_window.geometry("600x500")
        stats_window.configure(bg="#ffffff")
        stats_window.transient(self)
        
        # Crear notebook para pestañas
        notebook = ttk.Notebook(stats_window)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Pestaña de estadísticas generales
        general_frame = ttk.Frame(notebook)
        notebook.add(general_frame, text="General")
        
        # Pestaña de estadísticas por columna
        columns_frame = ttk.Frame(notebook)
        notebook.add(columns_frame, text="Por Columna")
        
        # Contenido de estadísticas generales
        stats_text = tk.Text(general_frame, wrap=tk.WORD, padx=10, pady=10)
        stats_scrollbar = ttk.Scrollbar(general_frame, orient="vertical", command=stats_text.yview)
        stats_text.configure(yscrollcommand=stats_scrollbar.set)
        
        # Calcular estadísticas
        stats_info = f"""ESTADÍSTICAS GENERALES
{'='*50}

Total de filas: {len(self.datos_originales)}
Total de columnas: {len(self.datos_originales.columns)}
Total de errores detectados: {self.total_errores}

INFORMACIÓN DE COLUMNAS:
{'-'*30}
"""
        
        for col in self.datos_originales.columns:
            try:
                if self.datos_originales[col].dtype in ['int64', 'float64']:
                    stats_info += f"\n{col}:"
                    stats_info += f"\n  - Tipo: Numérico"
                    stats_info += f"\n  - Valores únicos: {self.datos_originales[col].nunique()}"
                    stats_info += f"\n  - Valores nulos: {self.datos_originales[col].isnull().sum()}"
                    stats_info += f"\n  - Mínimo: {self.datos_originales[col].min()}"
                    stats_info += f"\n  - Máximo: {self.datos_originales[col].max()}"
                    stats_info += f"\n  - Promedio: {self.datos_originales[col].mean():.2f}"
                else:
                    stats_info += f"\n{col}:"
                    stats_info += f"\n  - Tipo: Texto"
                    stats_info += f"\n  - Valores únicos: {self.datos_originales[col].nunique()}"
                    stats_info += f"\n  - Valores nulos: {self.datos_originales[col].isnull().sum()}"
                stats_info += "\n"
            except:
                continue
        
        stats_text.insert(tk.END, stats_info)
        stats_text.configure(state=tk.DISABLED)
        
        stats_scrollbar.pack(side="right", fill="y")
        stats_text.pack(side="left", fill="both", expand=True)

    def crear_menu(self):
        """Crear menú principal mejorado"""
        # Agregar esto después de crear la ventana principal
        menubar = tk.Menu(self)
        self.config(menu=menubar)
        
        # Menú Archivo
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Archivo", menu=file_menu)
        file_menu.add_command(label="🆕 Nuevo", command=self.nuevo_archivo, accelerator="Ctrl+N")
        file_menu.add_command(label="📁 Abrir", command=self.buscar_archivo, accelerator="Ctrl+O")
        file_menu.add_separator()
        file_menu.add_command(label="💾 Guardar", command=self.guardar_archivo, accelerator="Ctrl+S")
        file_menu.add_command(label="📤 Exportar", command=self.exportar_datos)
        file_menu.add_command(label="📥 Importar", command=self.importar_datos)
        file_menu.add_separator()
        file_menu.add_command(label="❌ Salir", command=self.quit)
        
        # Menú Edición
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Edición", menu=edit_menu)
        edit_menu.add_command(label="📋 Copiar", command=self.copiar_portapapeles, accelerator="Ctrl+C")
        edit_menu.add_command(label="🗑️ Eliminar Fila", command=self.eliminar_fila, accelerator="Del")
        edit_menu.add_separator()
        edit_menu.add_command(label="🔍 Buscar", command=lambda: self.search_entry.focus())
        edit_menu.add_command(label="❌ Limpiar Filtros", command=self.limpiar_filtros)
        
        # Menú Herramientas
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Herramientas", menu=tools_menu)
        tools_menu.add_command(label="🔄 Actualizar", command=self.actualizar_datos, accelerator="F5")
        tools_menu.add_command(label="📈 Estadísticas", command=self.mostrar_estadisticas)
        
        # Menú Ver
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Ver", menu=view_menu)
        view_menu.add_command(label="🌙 Alternar Modo Oscuro", command=self.toggle_dark_mode)
        view_menu.add_command(label="❗ Marcar Errores", command=self.marcar_errores)
        
        # Menú Ayuda
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Ayuda", menu=help_menu)
        help_menu.add_command(label="📧 Contacto", command=self.mostrar_contacto)
        help_menu.add_command(label="ℹ️ Acerca de", command=self.mostrar_acerca_de)

    def nuevo_archivo(self):
        """Crear nuevo archivo"""
        if messagebox.askyesno("Nuevo Archivo", "¿Está seguro? Se perderán los datos no guardados."):
            self.datos_originales = None
            for item in self.tree.get_children():
                self.tree.delete(item)
            self.total_filas = 0
            self.total_errores = 0
            self.errores_indices = {}
            self.info_label.configure(text="Archivo: No seleccionado | Filas: 0 | Errores: 0", fg="#6b7280")
            self.update_status("Nuevo archivo creado")

    def mostrar_acerca_de(self):
        """Mostrar información del programa"""
        about_window = tk.Toplevel(self)
        about_window.title("Acerca de")
        about_window.geometry("400x350")
        about_window.configure(bg="#ffffff")
        about_window.resizable(False, False)
        about_window.transient(self)
        about_window.grab_set()
        
        # Centrar ventana
        about_window.update_idletasks()
        x = (about_window.winfo_screenwidth() // 2) - (400 // 2)
        y = (about_window.winfo_screenheight() // 2) - (350 // 2)
        about_window.geometry(f"400x350+{x}+{y}")
        
        # Logo/Icono
        tk.Label(
            about_window,
            text="📊",
            font=("Segoe UI", 48),
            bg="#ffffff",
            fg="#3b82f6"
        ).pack(pady=(20, 10))
        
        # Título
        tk.Label(
            about_window,
            text="Estructurador de Datos",
            font=("Segoe UI", 16, "bold"),
            bg="#ffffff",
            fg="#1f2937"
        ).pack()
        
        # Versión
        tk.Label(
            about_window,
            text="Versión 4.0 Professional",
            font=("Segoe UI", 12),
            bg="#ffffff",
            fg="#6b7280"
        ).pack(pady=(5, 20))
        
        # Descripción
        description = """Una herramienta profesional para el análisis,
edición y procesamiento de datos de algodón.

Características principales:
• Edición en línea de datos
• Búsqueda y filtrado avanzado
• Detección automática de errores
• Múltiples formatos de exportación
• Interfaz moderna y fácil de usar"""
        
        tk.Label(
            about_window,
            text=description,
            font=("Segoe UI", 10),
            bg="#ffffff",
            fg="#374151",
            justify="center"
        ).pack(pady=(0, 20))
        
        # Desarrollador
        tk.Label(
            about_window,
            text="Desarrollado por: Joaquin Pawlowski",
            font=("Segoe UI", 9),
            bg="#ffffff",
            fg="#6b7280"
        ).pack()
        
        # Botón cerrar
        tk.Button(
            about_window,
            text="Cerrar",
            command=about_window.destroy,
            bg="#3b82f6",
            fg="white",
            font=("Segoe UI", 10),
            relief="flat",
            bd=0,
            padx=20,
            pady=8,
            cursor="hand2"
        ).pack(pady=20)
