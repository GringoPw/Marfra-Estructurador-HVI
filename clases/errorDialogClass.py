import tkinter as tk
import webbrowser
import webbrowser
from datetime import datetime

class ErrorDialog:
    """Diálogo personalizado para mostrar errores de manera profesional"""
    
    def __init__(self, parent, title="Error", error_type="general", error_data=None):
        self.parent = parent
        self.title = title
        self.error_type = error_type
        self.error_data = error_data or {}
        self.result = None
        
        # Crear ventana modal
        self.dialog = tk.Toplevel(parent)
        self.setup_dialog()
        self.create_content()
        
    def setup_dialog(self):
        """Configurar la ventana del diálogo"""
        self.dialog.title(self.title)
        self.dialog.configure(bg="#ffffff")
        self.dialog.resizable(False, False)
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        # Determinar tamaño según tipo de error
        if self.error_type in ["file_read", "validation", "processing"]:
            width, height = 500, 400
        else:
            width, height = 400, 300
            
        self.dialog.geometry(f"{width}x{height}")
        
        # Centrar ventana
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (height // 2)
        self.dialog.geometry(f"{width}x{height}+{x}+{y}")
        
    def create_content(self):
        """Crear contenido del diálogo según el tipo de error"""
        if self.error_type == "file_read":
            self.create_file_read_error()
        elif self.error_type == "validation":
            self.create_validation_error()
        elif self.error_type == "processing":
            self.create_processing_error()
        elif self.error_type == "network":
            self.create_network_error()
        else:
            self.create_general_error()
            
    def create_file_read_error(self):
        """Error específico para lectura de archivos"""
        # Header con icono
        header_frame = tk.Frame(self.dialog, bg="#dc2626", height=70)
        header_frame.pack(fill="x")
        header_frame.pack_propagate(False)
        
        header_content = tk.Frame(header_frame, bg="#dc2626")
        header_content.pack(fill="both", expand=True, padx=20, pady=15)
        
        tk.Label(
            header_content,
            text="📄❌",
            font=("Segoe UI", 24),
            bg="#dc2626",
            fg="white"
        ).pack(side="left")
        
        tk.Label(
            header_content,
            text="Error al Leer Archivo",
            font=("Segoe UI", 16, "bold"),
            bg="#dc2626",
            fg="white"
        ).pack(side="left", padx=(15, 0))
        
        # Contenido principal
        main_frame = tk.Frame(self.dialog, bg="#ffffff")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Información del error
        error_info = tk.Frame(main_frame, bg="#fef2f2", relief="flat", bd=1)
        error_info.pack(fill="x", pady=(0, 15))
        
        info_content = tk.Frame(error_info, bg="#fef2f2")
        info_content.pack(fill="x", padx=15, pady=10)
        
        tk.Label(
            info_content,
            text="⚠️ Detalles del Error:",
            font=("Segoe UI", 11, "bold"),
            bg="#fef2f2",
            fg="#991b1b"
        ).pack(anchor="w")
        
        # Mensaje de error principal
        error_msg = self.error_data.get('message', 'Error desconocido al leer el archivo')
        tk.Label(
            info_content,
            text=error_msg,
            font=("Segoe UI", 10),
            bg="#fef2f2",
            fg="#7f1d1d",
            wraplength=450,
            justify="left"
        ).pack(anchor="w", pady=(5, 0))
        
        # Información adicional del archivo
        if 'file_path' in self.error_data:
            tk.Label(
                info_content,
                text=f"📁 Archivo: {self.error_data['file_path']}",
                font=("Segoe UI", 9),
                bg="#fef2f2",
                fg="#7f1d1d"
            ).pack(anchor="w", pady=(5, 0))
            
        if 'line_number' in self.error_data:
            tk.Label(
                info_content,
                text=f"📍 Línea: {self.error_data['line_number']}",
                font=("Segoe UI", 9),
                bg="#fef2f2",
                fg="#7f1d1d"
            ).pack(anchor="w", pady=(2, 0))
        
        # Sugerencias
        suggestions_frame = tk.Frame(main_frame, bg="#f0f9ff", relief="flat", bd=1)
        suggestions_frame.pack(fill="x", pady=(0, 15))
        
        sugg_content = tk.Frame(suggestions_frame, bg="#f0f9ff")
        sugg_content.pack(fill="x", padx=15, pady=10)
        
        tk.Label(
            sugg_content,
            text="💡 Sugerencias:",
            font=("Segoe UI", 11, "bold"),
            bg="#f0f9ff",
            fg="#0369a1"
        ).pack(anchor="w")
        
        suggestions = [
            "• Verifique que el archivo no esté corrupto",
            "• Asegúrese de que el formato sea compatible",
            "• Compruebe que el archivo no esté en uso por otra aplicación",
            "• Verifique los permisos de lectura del archivo"
        ]
        
        for suggestion in suggestions:
            tk.Label(
                sugg_content,
                text=suggestion,
                font=("Segoe UI", 9),
                bg="#f0f9ff",
                fg="#0c4a6e"
            ).pack(anchor="w", pady=(2, 0))
        
        self.create_action_buttons(main_frame)
        
    def create_validation_error(self):
        """Error específico para validación de datos"""
        # Header
        header_frame = tk.Frame(self.dialog, bg="#f59e0b", height=70)
        header_frame.pack(fill="x")
        header_frame.pack_propagate(False)
        
        header_content = tk.Frame(header_frame, bg="#f59e0b")
        header_content.pack(fill="both", expand=True, padx=20, pady=15)
        
        tk.Label(
            header_content,
            text="⚠️",
            font=("Segoe UI", 24),
            bg="#f59e0b",
            fg="white"
        ).pack(side="left")
        
        tk.Label(
            header_content,
            text="Errores de Validación",
            font=("Segoe UI", 16, "bold"),
            bg="#f59e0b",
            fg="white"
        ).pack(side="left", padx=(15, 0))
        
        # Contenido principal
        main_frame = tk.Frame(self.dialog, bg="#ffffff")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Resumen de errores
        summary_frame = tk.Frame(main_frame, bg="#fffbeb", relief="flat", bd=1)
        summary_frame.pack(fill="x", pady=(0, 15))
        
        summary_content = tk.Frame(summary_frame, bg="#fffbeb")
        summary_content.pack(fill="x", padx=15, pady=10)
        
        total_errors = self.error_data.get('total_errors', 0)
        error_types = self.error_data.get('error_types', {})
        
        tk.Label(
            summary_content,
            text=f"📊 Total de errores encontrados: {total_errors}",
            font=("Segoe UI", 11, "bold"),
            bg="#fffbeb",
            fg="#92400e"
        ).pack(anchor="w")
        
        # Desglose por tipo de error
        if error_types:
            tk.Label(
                summary_content,
                text="📋 Desglose de errores:",
                font=("Segoe UI", 10, "bold"),
                bg="#fffbeb",
                fg="#92400e"
            ).pack(anchor="w", pady=(10, 5))
            
            for error_type, count in error_types.items():
                tk.Label(
                    summary_content,
                    text=f"  • {error_type}: {count}",
                    font=("Segoe UI", 9),
                    bg="#fffbeb",
                    fg="#a16207"
                ).pack(anchor="w", pady=(1, 0))
        
        # Lista detallada de errores (scrollable)
        if 'error_list' in self.error_data:
            tk.Label(
                main_frame,
                text="📝 Detalle de errores:",
                font=("Segoe UI", 11, "bold"),
                bg="#ffffff",
                fg="#374151"
            ).pack(anchor="w", pady=(0, 5))
            
            # Frame con scrollbar
            list_frame = tk.Frame(main_frame, bg="#ffffff")
            list_frame.pack(fill="both", expand=True, pady=(0, 15))
            
            # Listbox con scrollbar
            listbox_frame = tk.Frame(list_frame, bg="#f9fafb", relief="flat", bd=1)
            listbox_frame.pack(fill="both", expand=True)
            
            scrollbar = tk.Scrollbar(listbox_frame)
            scrollbar.pack(side="right", fill="y")
            
            listbox = tk.Listbox(
                listbox_frame,
                yscrollcommand=scrollbar.set,
                font=("Segoe UI", 9),
                bg="#f9fafb",
                fg="#374151",
                selectbackground="#dbeafe",
                relief="flat",
                bd=0
            )
            listbox.pack(side="left", fill="both", expand=True)
            scrollbar.config(command=listbox.yview)
            
            for error in self.error_data['error_list']:
                if isinstance(error, dict):
                    error_text = f"Línea {error.get('line', '?')}: {error.get('message', 'Error desconocido')}"
                else:
                    error_text = str(error)
                listbox.insert(tk.END, error_text)
        
        self.create_action_buttons(main_frame)
        
    def create_processing_error(self):
        """Error específico para procesamiento de datos"""
        # Header
        header_frame = tk.Frame(self.dialog, bg="#8b5cf6", height=70)
        header_frame.pack(fill="x")
        header_frame.pack_propagate(False)
        
        header_content = tk.Frame(header_frame, bg="#8b5cf6")
        header_content.pack(fill="both", expand=True, padx=20, pady=15)
        
        tk.Label(
            header_content,
            text="⚙️❌",
            font=("Segoe UI", 24),
            bg="#8b5cf6",
            fg="white"
        ).pack(side="left")
        
        tk.Label(
            header_content,
            text="Error de Procesamiento",
            font=("Segoe UI", 16, "bold"),
            bg="#8b5cf6",
            fg="white"
        ).pack(side="left", padx=(15, 0))
        
        # Contenido principal
        main_frame = tk.Frame(self.dialog, bg="#ffffff")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Información del proceso
        process_info = tk.Frame(main_frame, bg="#faf5ff", relief="flat", bd=1)
        process_info.pack(fill="x", pady=(0, 15))
        
        info_content = tk.Frame(process_info, bg="#faf5ff")
        info_content.pack(fill="x", padx=15, pady=10)
        
        operation = self.error_data.get('operation', 'Operación desconocida')
        progress = self.error_data.get('progress', 0)
        
        tk.Label(
            info_content,
            text=f"🔄 Operación: {operation}",
            font=("Segoe UI", 11, "bold"),
            bg="#faf5ff",
            fg="#7c3aed"
        ).pack(anchor="w")
        
        tk.Label(
            info_content,
            text=f"📊 Progreso: {progress}%",
            font=("Segoe UI", 10),
            bg="#faf5ff",
            fg="#8b5cf6"
        ).pack(anchor="w", pady=(5, 0))
        
        # Error técnico
        if 'technical_error' in self.error_data:
            tech_frame = tk.Frame(main_frame, bg="#f1f5f9", relief="flat", bd=1)
            tech_frame.pack(fill="x", pady=(0, 15))
            
            tech_content = tk.Frame(tech_frame, bg="#f1f5f9")
            tech_content.pack(fill="x", padx=15, pady=10)
            
            tk.Label(
                tech_content,
                text="🔧 Error técnico:",
                font=("Segoe UI", 10, "bold"),
                bg="#f1f5f9",
                fg="#475569"
            ).pack(anchor="w")
            
            tk.Label(
                tech_content,
                text=self.error_data['technical_error'],
                font=("Consolas", 9),
                bg="#f1f5f9",
                fg="#64748b",
                wraplength=450,
                justify="left"
            ).pack(anchor="w", pady=(5, 0))
        
        self.create_action_buttons(main_frame)
        
    def create_network_error(self):
        """Error específico para problemas de red"""
        # Header
        header_frame = tk.Frame(self.dialog, bg="#ef4444", height=70)
        header_frame.pack(fill="x")
        header_frame.pack_propagate(False)
        
        header_content = tk.Frame(header_frame, bg="#ef4444")
        header_content.pack(fill="both", expand=True, padx=20, pady=15)
        
        tk.Label(
            header_content,
            text="🌐❌",
            font=("Segoe UI", 24),
            bg="#ef4444",
            fg="white"
        ).pack(side="left")
        
        tk.Label(
            header_content,
            text="Error de Conexión",
            font=("Segoe UI", 16, "bold"),
            bg="#ef4444",
            fg="white"
        ).pack(side="left", padx=(15, 0))
        
        # Contenido principal
        main_frame = tk.Frame(self.dialog, bg="#ffffff")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Información de conectividad
        conn_info = tk.Frame(main_frame, bg="#fef2f2", relief="flat", bd=1)
        conn_info.pack(fill="x", pady=(0, 15))
        
        info_content = tk.Frame(conn_info, bg="#fef2f2")
        info_content.pack(fill="x", padx=15, pady=10)
        
        tk.Label(
            info_content,
            text="🔌 Estado de conexión:",
            font=("Segoe UI", 11, "bold"),
            bg="#fef2f2",
            fg="#dc2626"
        ).pack(anchor="w")
        
        status = self.error_data.get('connection_status', 'Desconectado')
        tk.Label(
            info_content,
            text=f"  • Estado: {status}",
            font=("Segoe UI", 10),
            bg="#fef2f2",
            fg="#991b1b"
        ).pack(anchor="w", pady=(5, 0))
        
        if 'server_url' in self.error_data:
            tk.Label(
                info_content,
                text=f"  • Servidor: {self.error_data['server_url']}",
                font=("Segoe UI", 10),
                bg="#fef2f2",
                fg="#991b1b"
            ).pack(anchor="w", pady=(2, 0))
        
        self.create_action_buttons(main_frame)
        
    def create_general_error(self):
        """Error general/genérico"""
        # Header
        header_frame = tk.Frame(self.dialog, bg="#6b7280", height=70)
        header_frame.pack(fill="x")
        header_frame.pack_propagate(False)
        
        header_content = tk.Frame(header_frame, bg="#6b7280")
        header_content.pack(fill="both", expand=True, padx=20, pady=15)
        
        tk.Label(
            header_content,
            text="❌",
            font=("Segoe UI", 24),
            bg="#6b7280",
            fg="white"
        ).pack(side="left")
        
        tk.Label(
            header_content,
            text=self.title,
            font=("Segoe UI", 16, "bold"),
            bg="#6b7280",
            fg="white"
        ).pack(side="left", padx=(15, 0))
        
        # Contenido principal
        main_frame = tk.Frame(self.dialog, bg="#ffffff")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Mensaje de error
        message = self.error_data.get('message', 'Ha ocurrido un error inesperado')
        tk.Label(
            main_frame,
            text=message,
            font=("Segoe UI", 11),
            bg="#ffffff",
            fg="#374151",
            wraplength=350,
            justify="center"
        ).pack(pady=(20, 30))
        
        self.create_action_buttons(main_frame)
        
    def create_action_buttons(self, parent):
        """Crear botones de acción"""
        button_frame = tk.Frame(parent, bg="#ffffff")
        button_frame.pack(fill="x", side="bottom")
        
        # Botón de contacto (si está disponible)
        if hasattr(self.parent, 'mostrar_contacto'):
            tk.Button(
                button_frame,
                text="📧 Contactar Soporte",
                command=self.contactar_soporte,
                bg="#10b981",
                fg="white",
                font=("Segoe UI", 9),
                relief="flat",
                bd=0,
                padx=15,
                pady=8,
                cursor="hand2"
            ).pack(side="left")
        
        # Botón de reintento (si es aplicable)
        if self.error_type in ["file_read", "network", "processing"]:
            tk.Button(
                button_frame,
                text="🔄 Reintentar",
                command=self.reintentar,
                bg="#3b82f6",
                fg="white",
                font=("Segoe UI", 9),
                relief="flat",
                bd=0,
                padx=15,
                pady=8,
                cursor="hand2"
            ).pack(side="left", padx=(10, 0))
        
        # Botón cerrar
        tk.Button(
            button_frame,
            text="❌ Cerrar",
            command=self.cerrar_dialog,
            bg="#6b7280",
            fg="white",
            font=("Segoe UI", 9),
            relief="flat",
            bd=0,
            padx=15,
            pady=8,
            cursor="hand2"
        ).pack(side="right")
        
        # Botón de guardar log de error
        tk.Button(
            button_frame,
            text="💾 Guardar Log",
            command=self.guardar_log,
            bg="#8b5cf6",
            fg="white",
            font=("Segoe UI", 9),
            relief="flat",
            bd=0,
            padx=15,
            pady=8,
            cursor="hand2"
        ).pack(side="right", padx=(0, 10))
        
    def contactar_soporte(self):
        """Abrir contacto de soporte"""
        if hasattr(self.parent, 'mostrar_contacto'):
            self.parent.mostrar_contacto()
        else:
            webbrowser.open("mailto:joaquin.paw@gmail.com")
        
    def reintentar(self):
        """Acción de reintento"""
        self.result = "retry"
        self.cerrar_dialog()
        
    from datetime import datetime
    def guardar_log(self):
        from tkinter import filedialog

        filename = filedialog.asksaveasfilename(
            defaultextension=".log",
            filetypes=[("Log files", "*.log"), ("Text files", "*.txt")],
            title="Guardar log de error"
        )

        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write("=== LOG DE ERROR ===\n")
                    f.write(f"Fecha/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write(f"Tipo de error: {self.error_type}\n")
                    f.write(f"Título: {self.title}\n")
                    f.write("Datos del error:\n")
                    for key, value in self.error_data.items():
                        f.write(f"  - {key}: {value}\n")
            except Exception as e:
                print(f"Error al guardar el log: {e}")
    
    def cerrar_dialog(self):
        """Cerrar el diálogo"""
        if self.result is None:
            self.result = "close"
        self.dialog.destroy()
        
    def show_and_wait(self):
        """Mostrar el diálogo y esperar respuesta"""
        self.dialog.wait_window()
        return self.result

